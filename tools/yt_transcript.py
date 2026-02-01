#!/usr/bin/env python3
"""
YouTube Video Transcript Extractor

Extracts transcripts from YouTube videos using multiple methods:
1. youtube-transcript-api (captions/subtitles)
2. yt-dlp subtitle extraction
3. yt-dlp audio download + Whisper transcription (fallback)

Usage:
    python yt_transcript.py <video_url_or_id> [--method auto|captions|whisper] [--output <file>]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from URL or return as-is if already an ID."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id


def method_transcript_api(video_id: str) -> dict:
    """Method 1: Use youtube-transcript-api to get captions."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id)

        segments = []
        full_text_parts = []
        for entry in transcript_list:
            segments.append({
                "start": entry.start,
                "duration": entry.duration,
                "text": entry.text,
            })
            full_text_parts.append(entry.text)

        return {
            "method": "youtube-transcript-api",
            "video_id": video_id,
            "segment_count": len(segments),
            "segments": segments,
            "full_text": " ".join(full_text_parts),
        }
    except Exception as e:
        return {"method": "youtube-transcript-api", "error": str(e)}


def method_ytdlp_subtitles(video_id: str) -> dict:
    """Method 2: Use yt-dlp to download subtitles."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "subs")
        # Try auto-generated subtitles first, then manual
        for sub_flag in ["--write-auto-sub", "--write-sub"]:
            try:
                cmd = [
                    "yt-dlp",
                    "--skip-download",
                    sub_flag,
                    "--sub-lang", "en",
                    "--sub-format", "json3",
                    "--convert-subs", "json3",
                    "-o", output_template,
                    url,
                ]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=120
                )
                # Look for the subtitle file
                for f in Path(tmpdir).glob("*.json3"):
                    with open(f, "r") as fh:
                        data = json.load(fh)
                    segments = []
                    full_text_parts = []
                    for event in data.get("events", []):
                        text = ""
                        for seg in event.get("segs", []):
                            text += seg.get("utf8", "")
                        text = text.strip()
                        if text:
                            segments.append({
                                "start": event.get("tStartMs", 0) / 1000.0,
                                "duration": event.get("dDurationMs", 0) / 1000.0,
                                "text": text,
                            })
                            full_text_parts.append(text)
                    if segments:
                        return {
                            "method": f"yt-dlp ({sub_flag})",
                            "video_id": video_id,
                            "segment_count": len(segments),
                            "segments": segments,
                            "full_text": " ".join(full_text_parts),
                        }
                # Also check for .vtt or .srt
                for ext in ["*.vtt", "*.srt", "*.en.*"]:
                    for f in Path(tmpdir).glob(ext):
                        content = f.read_text()
                        if content.strip():
                            return {
                                "method": f"yt-dlp ({sub_flag}, raw)",
                                "video_id": video_id,
                                "raw_subtitles": content,
                                "full_text": _parse_vtt_to_text(content),
                            }
            except subprocess.TimeoutExpired:
                continue
            except Exception as e:
                continue

    return {"method": "yt-dlp subtitles", "error": "No subtitles found"}


def _parse_vtt_to_text(vtt_content: str) -> str:
    """Parse VTT/SRT content to plain text."""
    lines = vtt_content.split("\n")
    text_parts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("WEBVTT") or line.startswith("NOTE"):
            continue
        if re.match(r'^\d+$', line):
            continue
        if re.match(r'\d{2}:\d{2}', line):
            continue
        # Remove HTML tags
        line = re.sub(r'<[^>]+>', '', line)
        if line:
            text_parts.append(line)
    return " ".join(text_parts)


def method_whisper(video_id: str, model_size: str = "base") -> dict:
    """Method 3: Download audio with yt-dlp, transcribe with Whisper."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")
        try:
            # Download audio only
            cmd = [
                "yt-dlp",
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "0",
                "-o", audio_path,
                url,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                return {
                    "method": "whisper",
                    "error": f"yt-dlp download failed: {result.stderr[:500]}",
                }

            # Find the actual audio file (yt-dlp may rename)
            audio_files = list(Path(tmpdir).glob("audio*"))
            if not audio_files:
                return {"method": "whisper", "error": "No audio file produced"}
            actual_audio = str(audio_files[0])

            # Transcribe with faster-whisper
            from faster_whisper import WhisperModel

            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            segs, info = model.transcribe(actual_audio, language="en")

            segments = []
            full_text_parts = []
            for seg in segs:
                segments.append({
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text.strip(),
                })
                full_text_parts.append(seg.text.strip())

            return {
                "method": f"whisper ({model_size})",
                "video_id": video_id,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segment_count": len(segments),
                "segments": segments,
                "full_text": " ".join(full_text_parts),
            }
        except Exception as e:
            return {"method": "whisper", "error": str(e)}


def extract_transcript(video_url_or_id: str, method: str = "auto") -> dict:
    """
    Extract transcript using the specified method.

    Args:
        video_url_or_id: YouTube URL or video ID
        method: 'auto' (try all), 'captions' (API only), 'whisper' (audio transcription)

    Returns:
        dict with transcript data or error information
    """
    video_id = extract_video_id(video_url_or_id)
    print(f"[INFO] Video ID: {video_id}")

    if method in ("auto", "captions"):
        print("[INFO] Trying youtube-transcript-api...")
        result = method_transcript_api(video_id)
        if "error" not in result:
            print(f"[OK] Got {result['segment_count']} segments via transcript API")
            return result
        print(f"[WARN] transcript-api failed: {result['error']}")

    if method in ("auto", "captions"):
        print("[INFO] Trying yt-dlp subtitle extraction...")
        result = method_ytdlp_subtitles(video_id)
        if "error" not in result:
            print(f"[OK] Got subtitles via yt-dlp")
            return result
        print(f"[WARN] yt-dlp subtitles failed: {result['error']}")

    if method in ("auto", "whisper"):
        print("[INFO] Trying Whisper transcription (downloading audio)...")
        result = method_whisper(video_id)
        if "error" not in result:
            print(f"[OK] Transcribed {result['segment_count']} segments via Whisper")
            return result
        print(f"[WARN] Whisper failed: {result['error']}")

    return {
        "video_id": video_id,
        "error": "All extraction methods failed",
    }


def format_transcript(data: dict, fmt: str = "timestamped") -> str:
    """Format transcript data for output."""
    if "error" in data and "segments" not in data:
        return f"ERROR: {data['error']}"

    if fmt == "plain":
        return data.get("full_text", "")

    if fmt == "timestamped":
        lines = []
        for seg in data.get("segments", []):
            start = seg.get("start", 0)
            minutes = int(start // 60)
            seconds = int(start % 60)
            lines.append(f"[{minutes:02d}:{seconds:02d}] {seg['text']}")
        return "\n".join(lines)

    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)

    return data.get("full_text", "")


def main():
    parser = argparse.ArgumentParser(
        description="Extract transcripts from YouTube videos"
    )
    parser.add_argument(
        "video", help="YouTube video URL or ID"
    )
    parser.add_argument(
        "--method", choices=["auto", "captions", "whisper"],
        default="auto", help="Extraction method (default: auto)"
    )
    parser.add_argument(
        "--format", choices=["timestamped", "plain", "json"],
        default="timestamped", help="Output format (default: timestamped)"
    )
    parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--whisper-model", default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size for audio transcription (default: base)"
    )

    args = parser.parse_args()

    data = extract_transcript(args.video, method=args.method)
    output = format_transcript(data, fmt=args.format)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"\n[SAVED] Transcript written to {args.output}")
        # Also save JSON metadata alongside
        meta_path = Path(args.output).with_suffix(".meta.json")
        meta_path.write_text(json.dumps({
            "video_id": data.get("video_id"),
            "method": data.get("method"),
            "segment_count": data.get("segment_count"),
            "duration": data.get("duration"),
        }, indent=2), encoding="utf-8")
        print(f"[SAVED] Metadata written to {meta_path}")
    else:
        print("\n" + "=" * 60)
        print(output)


if __name__ == "__main__":
    main()
