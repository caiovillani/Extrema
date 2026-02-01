# Claude Code Playbook

## Based on Nate Herk's "Master 95% of Claude Code in 36 Mins" Tutorial

### Compiled from video analysis, AI Automation Society resources, and official Anthropic documentation

---

## Table of Contents

1. [Overview and Philosophy](#1-overview-and-philosophy)
2. [The WAT Framework](#2-the-wat-framework)
3. [Environment Setup](#3-environment-setup)
4. [The claude.md System Prompt](#4-the-claudemd-system-prompt)
5. [Bypass Permissions Mode](#5-bypass-permissions-mode)
6. [Plan Mode](#6-plan-mode)
7. [The Golden Prompts](#7-the-golden-prompts)
8. [MCP Servers (Model Context Protocol)](#8-mcp-servers-model-context-protocol)
9. [Skills System](#9-skills-system)
10. [Debugging and Self-Healing](#10-debugging-and-self-healing)
11. [Deployment with Modal](#11-deployment-with-modal)
12. [Security Review Protocol](#12-security-review-protocol)
13. [Complete Workflow Example: YouTube Analytics Agent](#13-complete-workflow-example-youtube-analytics-agent)
14. [Essential Commands Reference](#14-essential-commands-reference)
15. [Best Practices and Anti-Patterns](#15-best-practices-and-anti-patterns)
16. [Video Timestamped Breakdown](#16-video-timestamped-breakdown)

---

## 1. Overview and Philosophy

### The Core Thesis

Nate Herk's central argument is that AI coding is shifting from **"Chat"** (asking questions, getting snippets) to **"Agency"** (autonomous multi-step execution). Claude Code is not a chatbot -- it is an **agentic coding environment** that can read your files, write code, execute commands, install dependencies, run tests, and iterate on failures without human intervention at every step.

### Who is Nate Herk?

- Founder & CEO of **Uppit AI** (formerly TrueHorizon AI)
- Runs the **"Nate Herk | AI Automation"** YouTube channel (172,000+ subscribers)
- Left Goldman Sachs to focus on AI automation systems
- Operates the **AI Automation Society** community on Skool (3,500+ members)
- Specializes in no-code and low-code AI automation workflows

### Key Distinction: Agentic Coding vs. Chat Coding

| Aspect | Chat Coding | Agentic Coding |
|--------|-------------|----------------|
| Interaction | Ask question, get snippet | Define goal, agent executes |
| Control flow | Human decides every step | Agent decides execution path |
| Error handling | Human debugs manually | Agent self-heals and retries |
| Scope | Single file, single function | Multi-file, full projects |
| Speed | Minutes per iteration | Seconds per iteration |

---

## 2. The WAT Framework

The WAT Framework is Nate's organizational architecture for building reliable AI automations. It separates **probabilistic reasoning** (AI) from **deterministic execution** (code).

### Layer 1: Workflows (W)

- **Format**: Markdown files (`.md`)
- **Location**: `/workflows/` directory
- **Purpose**: SOPs (Standard Operating Procedures) written in plain English
- **Content**: What needs to be done, the order of operations, how to handle failures
- **Analogy**: The instruction manual that the agent reads

**Example workflow file** (`/workflows/youtube_weekly.md`):

```markdown
# YouTube Weekly Analytics Workflow

## Trigger
- Schedule: Every Monday at 6:00 AM EST

## Steps
1. Fetch trending videos from target channels (AI niche)
2. Collect metrics: views, likes, comments, publish date
3. Analyze trends: what topics are performing well
4. Generate charts and visualizations
5. Compile into branded PDF report
6. Email report to team via Gmail

## Error Handling
- If YouTube API quota exceeded: wait 1 hour, retry
- If email fails: save report locally, notify via fallback
```

### Layer 2: Agents (A)

- **Engine**: Claude Code (the reasoning layer)
- **Role**: Reads the workflow, decides how to execute it, coordinates tools
- **Behavior**: Interprets instructions, makes decisions, handles branching logic
- **Key Trait**: Probabilistic -- uses judgment to fill gaps in instructions

### Layer 3: Tools (T)

- **Format**: Python scripts (`.py`)
- **Location**: `/tools/` directory
- **Purpose**: Deterministic execution units that perform specific actions
- **Examples**: `scrape_youtube.py`, `send_email.py`, `generate_charts.py`
- **Key Trait**: Deterministic -- given same input, always produces same output

### Why This Separation Matters

```
Human writes Workflow (what) -->
Agent reads Workflow and coordinates (how) -->
Tools execute actions (do)
```

By separating concerns:
- Workflows are easy for humans to read, write, and modify
- The agent handles the complex coordination logic
- Tools are testable, debuggable, and reusable
- Failures can be isolated to the correct layer

### Folder Structure

```
project_root/
|-- claude.md              # System prompt / project config
|-- .env                   # API keys (never committed)
|-- workflows/
|   |-- youtube_weekly.md  # SOP for weekly analysis
|   |-- email_report.md    # SOP for email delivery
|-- tools/
|   |-- scrape_youtube.py  # YouTube Data API integration
|   |-- analyze_data.py    # Data processing and charting
|   |-- generate_pdf.py    # PDF report generation
|   |-- send_email.py      # Gmail API integration
|-- temp/                  # Temporary/intermediate files
|-- output/                # Final deliverables
```

---

## 3. Environment Setup

### Step 1: Install VS Code

Download and install Visual Studio Code from [code.visualstudio.com](https://code.visualstudio.com/).

### Step 2: Install Claude Code

**Option A -- VS Code Extension** (shown in video):
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Claude Code" by Anthropic
4. Install the extension

**Option B -- Native CLI Install** (recommended by Anthropic):

```bash
# macOS, Linux, WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

### Step 3: Authentication

- Requires a **paid Anthropic plan**: Claude Pro ($20/mo) or Claude Max ($100/mo)
- Sign in through the extension or CLI when prompted
- Credentials are stored locally after first login

### Step 4: Interface Layout (VS Code)

- **Left Panel**: File Explorer -- your project's file structure (workflows, tools, prompts)
- **Right Panel**: Agent Chat -- the conversational interface where you interact with Claude Code

---

## 4. The claude.md System Prompt

### What It Is

The `claude.md` file is the **system prompt** for your project. It lives in the root of your project directory. Without it, Claude Code behaves generically. With it, Claude understands your project's architecture, coding philosophy, folder conventions, and constraints.

### Why It Matters

- Every time Claude Code starts a session, it reads `claude.md` first
- It acts as persistent memory across sessions
- It defines the rules of engagement for the entire project

### Template (Reconstructed from Nate's Video)

```markdown
# Project Configuration

## Role
You are an autonomous developer working in the WAT framework.

## Folder Rules
- Store workflows in /workflows (Markdown SOPs)
- Store tools in /tools (Python scripts)
- Store temporary files in /temp
- Store final outputs in /output

## Architecture
- Layer 1 (Workflows): Markdown files that define step-by-step processes
- Layer 2 (Agent): You, Claude Code, coordinating execution
- Layer 3 (Tools): Python scripts for API calls, data processing, file generation

## Coding Standards
- Use Python 3.10+
- Include error handling in all API calls
- Store API keys in .env (never hardcode)
- Write modular, reusable functions
- Add docstrings to all public functions

## Communication Style
- Ask clarifying questions before building
- Propose a plan before coding
- Report progress after each major step
```

### Hierarchy of claude.md Files

Claude Code supports multiple levels of configuration:

| File | Scope | Use Case |
|------|-------|----------|
| `~/.claude/CLAUDE.md` | Global (all projects) | Personal preferences, global rules |
| `/project/CLAUDE.md` | Project-wide | Project architecture, coding standards |
| `/project/src/CLAUDE.md` | Directory-specific | Module-specific instructions |

---

## 5. Bypass Permissions Mode

### The Problem

By default, Claude Code asks for explicit permission before every file edit, every command execution, every dependency installation. This is safe but **extremely slow** for iterative development.

### The Solution

Enable "Bypass Permissions" to allow the agent to act autonomously.

### How to Enable

**In VS Code:**
1. Open Settings (Cmd+, or Ctrl+,)
2. Search for "Claude Code"
3. Check: **"Allow Bypass Permissions Mode"**

**In CLI:**
- Use the `--dangerously-skip-permissions` flag (for scripted/automated use)

### What Changes

| Without Bypass | With Bypass |
|----------------|-------------|
| "Can I edit main.py?" -- waits for approval | Edits main.py immediately |
| "Can I run pip install?" -- waits for approval | Installs dependencies immediately |
| "Can I create this file?" -- waits for approval | Creates file immediately |

### Why Nate Calls It "The Secret Sauce"

- Eliminates human bottlenecks during rapid iteration
- Enables true self-healing: agent can detect error, fix code, re-run, all without asking
- Reduces a 30-minute build to minutes
- The agent can complete entire multi-step workflows autonomously

### Safety Considerations

- Only enable in development environments
- Never enable on production systems
- Review the agent's work after autonomous sessions
- Keep version control (git) active so you can revert changes

---

## 6. Plan Mode

### What It Is

Plan Mode is a special mode in Claude Code that makes the model **think deeper and research before coding**. Instead of immediately writing code, it:

1. Analyzes the request thoroughly
2. Researches available APIs, libraries, and approaches
3. Asks clarifying questions
4. Proposes an architecture
5. Waits for approval before building

### How to Activate

In the Claude Code chat, type:

```
/plan
```

### When to Use Plan Mode

- Starting a new project or major feature
- Building complex multi-step automations
- When you need the agent to research APIs or libraries
- When architecture decisions need to be made upfront

### The Negotiation Phase

After entering Plan Mode and submitting a prompt, Claude will engage in a **negotiation**:

1. Claude asks clarifying questions about scope, frequency, delivery format
2. You answer, refining the requirements
3. Claude proposes an architecture and asks for approval
4. You approve or modify
5. Claude generates a to-do list and begins building

**Example negotiation from the video:**

```
Claude: "How frequently should this run?"
Nate: "Weekly"

Claude: "Where should the data be stored?"
Nate: "Google Sheets"

Claude: "Should I auto-discover channels or use a predefined list?"
Nate: "Auto-discover channels in the AI niche"

Claude: "What format for the final deliverable?"
Nate: "Email via Gmail"
```

---

## 7. The Golden Prompts

These are the exact prompts Nate used in the video, documented verbatim.

### Prompt 1: Initialization

**Context**: Used after creating the `claude.md` file to bootstrap the project structure.

```
Initialize this project based on the claude.md file
```

**What happens**: Claude reads `claude.md`, creates the folder structure (`/workflows`, `/tools`, `/temp`), and sets up the project skeleton.

### Prompt 2: Plan Mode -- Project Definition

**Context**: Used in `/plan` mode to define the YouTube Analytics Scraper project.

```
Hey Claude I need your help building an automation i want this automation
to basically scrape tons of YouTube videos and YouTube channels in my
niche which is AI and AI automation i want to get insights about what
videos are trending what's working well and kind of what the AI space is
feeling like so that I can create more content that people want to see
and that will be beneficial for them i need your help understanding how
we can actually get this data so look into different APIs or MCP servers
also let me know if there's any skills that would be helpful because
after you've done this research what I want you to do is I want you to
create a slide deck for me so I want to get an actual deliverable that
will be sent to my email using Gmail and it should be a really nice
professional look slide deck with charts and images and all of these
different graphics so that I can understand what's going on in the
industry so that's what I've got let me know if you have any questions
or if you have any recommendations for things that I haven't thought
of about this automation system
```

### Prompt 3: Skill Integration -- PDF Upgrade

**Context**: Used after installing the "Canvas Design" skill to upgrade output quality.

```
Hey Claude so I just gave you a skill for canvas design and instead of
outputting a PowerPoint presentation I want you to now take the same
research when you do your analysis from YouTube videos but I want you
to use that canvas design skill to create a PDF it needs to be
professional but it needs to be aesthetically pleasing and what I want
you to do is make sure you're including the AIS Plus logo PNG that I
dropped in this folder as well because I want the whole presentation
to be branded so I can share it with my team
```

### Prompt 4: Deployment to Modal

**Context**: Used to push the local automation to cloud for scheduled execution.

```
awesome i want to push the YouTube analytics workflow to modal so that
it can actually run every single Monday at 6 a.m
```

### Prompt 5: Security Review

**Context**: Used before deployment to check for exposed secrets.

```
check the code and let me know if there are any risks
```

### Prompt 6: Debugging (Implicit from Video)

**Context**: Used when the first PDF output only had 2 pages instead of the expected full report.

```
It was only two slides.
```

**What happens**: Claude analyzes the error, refactors the PDF generation script, and produces a correct 9-page PDF with the logo embedded.

---

## 8. MCP Servers (Model Context Protocol)

### What They Are

MCP Servers are **universal connectors** that allow Claude Code to interact with external services without writing custom API integration code. Nate describes them as **"universal USB ports"** or an **"App Store for AI."**

### How They Work

```
Claude Code  <-->  MCP Server  <-->  External Service
(Agent)           (Connector)        (Gmail, Sheets, Slack, etc.)
```

### Available MCP Servers (Examples)

| Service | Capability |
|---------|-----------|
| Gmail | Send/read emails, manage labels |
| Google Sheets | Read/write spreadsheet data |
| Google Calendar | Create/read events |
| Slack | Send messages, read channels |
| GitHub | Manage repos, PRs, issues |
| n8n | Create/edit/manage workflows |
| File System | Read/write local files |

### Installation

MCP servers are typically installed via Claude Code configuration:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-gmail"]
    },
    "google-sheets": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-google-sheets"]
    }
  }
}
```

### Key Benefit

Instead of writing 200 lines of OAuth + API code for Gmail, you install the MCP server and Claude can send emails with a simple tool call. The MCP handles authentication, rate limits, and error handling.

---

## 9. Skills System

### What Skills Are

Skills are **dynamic, reusable instruction sets** (custom prompts) that Claude loads **only when needed**. They extend Claude's capabilities with specialized knowledge.

### Types of Skills

| Type | Scope | Storage |
|------|-------|---------|
| Local Skills | Single project | `/project/.claude/skills/` |
| Global Skills | All projects | `~/.claude/skills/` |

### How Skills Work

1. A skill is a Markdown file with specialized instructions
2. When Claude encounters a task that matches a skill, it loads the instructions
3. The skill provides domain-specific knowledge and patterns

### Example: Canvas Design Skill

As used in the video, the Canvas Design skill:
- Teaches Claude how to generate professional PDF layouts
- Provides design principles (spacing, typography, color schemes)
- Includes templates for branded reports
- Handles logo placement and chart formatting

### Installing Skills

Skills can be installed from community repositories or created manually:

```bash
# Community skill installation (example)
claude skill install canvas-design

# Manual creation
mkdir -p .claude/skills
# Then create .claude/skills/canvas_design.md with instructions
```

### Creating Custom Skills

```markdown
# Skill: Canvas Design

## Trigger
When the user requests a PDF report or visual document.

## Instructions
1. Use reportlab or similar library for PDF generation
2. Apply professional layout:
   - Header with logo (top-left)
   - Title section with date
   - Charts with consistent color palette
   - Page numbers in footer
3. Color palette: #1a1a2e, #16213e, #0f3460, #e94560
4. Font hierarchy: Title (24pt), Heading (18pt), Body (12pt)
5. Include table of contents for reports > 5 pages
```

---

## 10. Debugging and Self-Healing

### The Self-Healing Loop

One of the most powerful capabilities demonstrated in the video is Claude Code's ability to **self-heal** when errors occur:

```
1. Agent runs code
2. Error occurs
3. Agent reads error message
4. Agent diagnoses root cause
5. Agent modifies code
6. Agent re-runs code
7. Repeat until success
```

### Example from the Video

**Problem**: First PDF attempt produced only 2 pages instead of a full report.

**Self-healing sequence**:
1. Nate reports: "It was only two slides"
2. Claude analyzes the PDF generation code
3. Identifies that the data pipeline was only passing partial data to the PDF renderer
4. Refactors the Python script to process all data sections
5. Re-generates the PDF: 9 pages with correct branding

### Why Bypass Permissions Enables Self-Healing

Without bypass permissions:
```
Error occurs --> Agent asks "Can I edit the file?" --> Wait for human -->
Human approves --> Agent edits --> Agent asks "Can I run the script?" -->
Wait for human --> Human approves --> Agent runs --> (repeat for each fix)
```

With bypass permissions:
```
Error occurs --> Agent edits file --> Agent runs script -->
Error persists --> Agent edits again --> Agent runs again --> Success
```

### Advanced: Self-Healing n8n Workflows

Nate demonstrates a more advanced pattern where:
1. An n8n workflow throws an error
2. An error-handler workflow triggers automatically
3. The error handler calls Claude Code via API
4. Claude uses the n8n MCP server to inspect the broken workflow
5. Claude identifies the issue and fixes the workflow
6. No human intervention required

---

## 11. Deployment with Modal

### What is Modal?

Modal is a **serverless Python infrastructure platform** that allows you to deploy local scripts to the cloud. It handles:
- Container orchestration
- CRON scheduling
- GPU allocation (if needed)
- Secrets management
- Auto-scaling

### Why Not Just Run Locally?

- Your computer needs to be on 24/7
- Local network issues can break automation
- No redundancy or failover
- Cannot scale

### Setup

```bash
# Install Modal client
pip install modal

# Authenticate
modal setup
```

### Deployment Pattern

Claude Code wraps your Python tools into a Modal app:

```python
import modal

app = modal.App("youtube-analytics")

@app.function(
    schedule=modal.Cron("0 6 * * 1"),  # Monday at 6 AM
    secrets=[modal.Secret.from_name("youtube-api-keys")]
)
def run_weekly_analysis():
    # Your pipeline code here
    scrape_channels()
    analyze_data()
    generate_report()
    send_email()
```

### CRON Expression Reference

```
0 6 * * 1   = Every Monday at 6:00 AM
0 9 * * *   = Every day at 9:00 AM
0 */6 * * * = Every 6 hours
0 0 1 * *   = First day of every month at midnight
```

### Secrets Management

API keys are stored as **Modal Secrets**, never hardcoded:

```bash
modal secret create youtube-api-keys \
  YOUTUBE_API_KEY=your_key_here \
  GMAIL_CLIENT_ID=your_id_here \
  GMAIL_CLIENT_SECRET=your_secret_here
```

### Alternative: Webhook Trigger

Instead of a CRON schedule, you can deploy as a webhook:

```python
@app.function()
@modal.web_endpoint(method="POST")
def webhook_trigger(request):
    data = request.json()
    run_analysis(data["company"])
    send_report(data["email"])
    return {"status": "success"}
```

Then trigger via Postman, n8n, or any HTTP client.

---

## 12. Security Review Protocol

### Before Any Deployment

Always run a security review before deploying to production:

```
check the code and let me know if there are any risks
```

### What Claude Checks

1. **Hardcoded secrets**: API keys, passwords, tokens in source code
2. **Exposed endpoints**: Unprotected webhooks or APIs
3. **Dependency vulnerabilities**: Known CVEs in installed packages
4. **Data leakage**: Personal data or sensitive info in logs/output
5. **Permission scope**: Excessive API permissions (principle of least privilege)

### Security Checklist

- [ ] API keys stored in environment variables or secrets manager (never in code)
- [ ] `.env` file listed in `.gitignore`
- [ ] OAuth tokens use minimal required scopes
- [ ] Webhook endpoints validate request origin
- [ ] Error messages don't expose internal details
- [ ] Dependencies are pinned to specific versions
- [ ] No personal data in logs or temporary files

---

## 13. Complete Workflow Example: YouTube Analytics Agent

This section reconstructs the full workflow built in the video.

### Phase 1: Bootstrap

```bash
# Create project folder
mkdir youtube_analysis
cd youtube_analysis

# Create claude.md (see Section 4 for template)
# Open in VS Code
code .
```

In Claude Code chat:
```
Initialize this project based on the claude.md file
```

### Phase 2: Plan

Switch to Plan Mode:
```
/plan
```

Enter the project definition prompt (see Prompt 2 in Section 7).

Answer Claude's clarifying questions:
- Frequency: Weekly
- Data storage: Google Sheets
- Channel discovery: Auto-discover in AI niche
- Deliverable: Email via Gmail
- Format: Professional slide deck / PDF

### Phase 3: Build

Claude autonomously generates:

**Tools created** (7 Python scripts in `/tools/`):
1. `channel_discovery.py` -- Find AI/automation YouTube channels
2. `video_scraper.py` -- Fetch video data via YouTube Data API v3
3. `metrics_collector.py` -- Aggregate views, likes, comments, engagement rates
4. `trend_analyzer.py` -- Identify trending topics and patterns
5. `chart_generator.py` -- Create matplotlib/plotly visualizations
6. `report_generator.py` -- Compile data into PDF report
7. `email_sender.py` -- Send report via Gmail API

**Workflow created** (`/workflows/youtube_weekly.md`):
- Step-by-step SOP for the entire pipeline

**Configuration**:
- `.env` file for API keys
- `requirements.txt` with dependencies

### Phase 4: Dependencies

Claude automatically installs:
```bash
pip install google-auth google-api-python-client
pip install matplotlib plotly reportlab
pip install python-dotenv
```

### Phase 5: First Test Run

Claude runs the data collection pipeline:
- Scrapes 30 channels
- Generates charts
- Creates initial PowerPoint
- Sends via Gmail

### Phase 6: Refinement

Install Canvas Design skill, add logo file, and use Prompt 3 (Section 7) to upgrade from PowerPoint to branded PDF.

### Phase 7: Debug

First PDF attempt: only 2 pages. Report the issue:
```
It was only two slides.
```
Claude self-heals and produces a correct 9-page branded PDF.

### Phase 8: Security Review

```
check the code and let me know if there are any risks
```

Claude confirms keys will be stored as Modal Secrets.

### Phase 9: Deploy

```
awesome i want to push the YouTube analytics workflow to modal so that
it can actually run every single Monday at 6 a.m
```

Claude writes the deployment script and schedules the app.

### Phase 10: Troubleshoot Production

If errors occur in production (e.g., "Quota Exceeded"):
1. Copy error log from Modal dashboard
2. Paste into Claude Code chat
3. Claude explains the issue and proposes a fix

---

## 14. Essential Commands Reference

### Claude Code CLI Commands

| Command | Description |
|---------|-------------|
| `claude` | Start interactive session |
| `claude "task"` | Run a one-time task |
| `claude -p "query"` | Run query and exit |
| `claude -c` | Continue most recent conversation |
| `claude -r` | Resume a previous conversation |
| `claude commit` | Create a Git commit |

### In-Session Commands

| Command | Description |
|---------|-------------|
| `/plan` | Switch to Plan Mode (think before coding) |
| `/clear` | Clear conversation history |
| `/help` | Show available commands |
| `/login` | Switch accounts |
| `/resume` | Continue a previous conversation |
| `exit` or Ctrl+C | Exit Claude Code |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `?` | Show all shortcuts |
| Tab | Command completion |
| Up Arrow | Command history |
| `/` | Show all commands and skills |

---

## 15. Best Practices and Anti-Patterns

### Best Practices

1. **Always create `claude.md` first** -- It is the foundation of every project. Without it, Claude operates without context.

2. **Use Plan Mode for new projects** -- Invest time upfront in planning. The negotiation phase prevents wasted iterations.

3. **Be specific in prompts** -- Instead of "fix the bug," say "fix the login bug where users see a blank screen after entering wrong credentials."

4. **Let Claude explore first** -- Before making changes, let Claude analyze and understand the codebase.

5. **Use the WAT separation** -- Keep workflows (Markdown), agent logic (Claude), and tools (Python) in separate layers.

6. **Security review before deployment** -- Always check for exposed keys, excessive permissions, and dependency vulnerabilities.

7. **Version control everything** -- Git protects you when the agent makes mistakes.

8. **Break complex tasks into steps** -- Multi-step instructions with numbered lists get better results than vague goals.

9. **Use Skills for repeated patterns** -- If you find yourself giving the same instructions repeatedly, create a skill.

10. **Monitor production deployments** -- Check logs on Modal/cloud dashboard after initial deployment.

### Anti-Patterns (What NOT to Do)

1. **Don't skip `claude.md`** -- A generic agent produces generic results.

2. **Don't enable bypass permissions in production** -- Only use it in development environments.

3. **Don't hardcode API keys** -- Always use `.env` files or secrets managers.

4. **Don't ignore Claude's questions** -- The negotiation phase is where architecture decisions happen. Skipping it leads to rework.

5. **Don't deploy without security review** -- One exposed API key can be catastrophic.

6. **Don't expect perfection on first try** -- Self-healing is a feature. Report errors clearly and let Claude iterate.

7. **Don't build monoliths** -- Keep tools small and modular. One script per action.

8. **Don't skip testing locally** -- Always test the full pipeline locally before deploying to cloud.

---

## 16. Video Timestamped Breakdown

Detailed chronological summary of the "Master 95% of Claude Code in 36 Mins" video.

| Timestamp | Topic | Key Content |
|-----------|-------|-------------|
| **[00:00]** | Introduction | Claude Code reduces hours of coding to minutes. Contrasts with no-code tools (n8n). Introduces "Agentic Coding." |
| **[01:21]** | Installation | Download VS Code. Install "Claude Code" extension by Anthropic. Requirement: paid Anthropic plan (Pro or Max). |
| **[02:50]** | The Interface | Left panel = File Explorer (code files). Right panel = Agent Chat (conversation with Claude). |
| **[04:30]** | The claude.md File | Every project needs a system prompt. Without `claude.md`, the agent is generic. With it, the agent understands file structure and coding philosophy. |
| **[05:03]** | WAT Framework | **W** = Workflows (Markdown SOPs). **A** = Agents (the coordinator/reasoning engine). **T** = Tools (Python execution scripts). Separates probabilistic reasoning from deterministic execution. |
| **[09:41]** | Bypass Permissions | Settings > Claude Code > "Allow Bypass Permissions." Stops the agent from asking permission 50 times. Enables autonomous self-healing iteration. |
| **[10:43]** | Plan Mode | `/plan` command. Makes the model think harder and research before coding. Nate enters the YouTube Analytics Scraper prompt. |
| **[13:15]** | The Negotiation | Claude asks clarifying questions: frequency, email destination, data storage format. Nate answers: auto-discover channels, weekly, Google Sheets, Gmail delivery. |
| **[14:11]** | Automated Building | Claude generates the to-do list and begins writing code. Creates `/tools/` folder with 7 Python scripts. Creates `/workflows/` folder with master Markdown guide. |
| **[15:43]** | Dependencies & Keys | Agent detects need for `google-auth` and `google-api-python-client`. Installs them automatically. Asks for YouTube API key; Nate pastes it into chat. |
| **[16:21]** | First Test Run | Agent runs "Data Collection Pipeline." Scrapes 30 channels. Generates charts. Creates a PowerPoint. Emails to Nate. |
| **[19:00]** | MCPs and Skills | MCP = "universal USB ports" for AI. Skills = dynamic instructions loaded on demand. Nate installs "Canvas Design" skill. |
| **[23:42]** | Refactoring for PDF | Uploads AIS Plus logo (PNG). Instructs Claude to switch from PowerPoint to branded PDF using the Design Skill. |
| **[26:51]** | Debugging & Self-Healing | First PDF: only 2 pages. Nate reports the issue. Claude analyzes, refactors, produces correct 9-page branded PDF. |
| **[28:58]** | Deployment (Modal) | Running locally is bad for automation (computer must stay on). Introduces Modal for serverless cloud hosting. |
| **[30:59]** | Security Review | Nate asks Claude to check for exposed API keys. Claude confirms keys will be stored as "Modal Secrets," not hardcoded. |
| **[31:34]** | Final Deployment | Agent writes deployment script. Schedules app for every Monday at 6 AM. Nate verifies on Modal dashboard. |
| **[33:12]** | Production Troubleshooting | Manual test on Modal fails. Error: "Quota Exceeded." Nate pastes error log into Claude Code. Claude explains they hit YouTube API daily limit from excessive testing. |
| **[33:53]** | Webhook Trigger | Alternative to CRON: webhook trigger. Nate sends a POST request via Postman. Triggers agent to research a company and send email. |

---

## Appendix A: Nate Herk's Resource Ecosystem

| Resource | URL | Description |
|----------|-----|-------------|
| YouTube Channel | Nate Herk \| AI Automation | 172K+ subscribers, tutorials on AI automation |
| Skool Community | AI Automation Society | Free community with resources and templates |
| Skool Premium | AI Automation Society Plus | Paid community ($94/mo) with courses, workshops |
| Agency | Uppit AI (nateherk.com) | Custom AI solutions for businesses |
| Newsletter | Nate's Newsletter (Substack) | "The Claude Code Complete Guide" and more |

## Appendix B: API Keys Required for the YouTube Analytics Agent

| Service | Key Type | How to Obtain |
|---------|----------|---------------|
| YouTube Data API v3 | API Key | Google Cloud Console > APIs & Services |
| Gmail API | OAuth 2.0 Client | Google Cloud Console > OAuth Consent Screen |
| Google Sheets API | OAuth 2.0 Client | Same OAuth setup as Gmail |
| Modal | Auth Token | `modal setup` (CLI authentication) |

## Appendix C: Glossary

| Term | Definition |
|------|-----------|
| **Agentic Coding** | AI autonomously executing multi-step coding tasks with minimal human intervention |
| **claude.md** | Project-level system prompt file that configures Claude Code's behavior |
| **Bypass Permissions** | Mode that allows Claude Code to edit files and run commands without asking for approval each time |
| **Plan Mode** | Claude Code mode that prioritizes research and architecture before coding |
| **WAT Framework** | Workflows-Agents-Tools: three-layer architecture for AI automation |
| **MCP** | Model Context Protocol: universal connector standard for AI-to-service integration |
| **Skills** | Reusable instruction sets that extend Claude Code's capabilities |
| **Modal** | Serverless Python cloud platform for deploying scripts with CRON/webhook triggers |
| **Self-Healing** | Agent's ability to detect errors, diagnose root causes, and fix code autonomously |
| **SOP** | Standard Operating Procedure: the plain-English workflow document |

---

## Disclaimer

This playbook was compiled from:
- The detailed text summary provided by the user (based on Nate Herk's "Master 95% of Claude Code in 36 Mins" video)
- Web research across AI Automation Society (Skool), Nate Herk's Substack, GitHub repositories, and Anthropic's official Claude Code documentation
- Cross-referencing with official Claude Code quickstart and best practices documentation

**Note on video transcript**: The full original video transcript was not publicly available online at the time of compilation. YouTube's environment was inaccessible from this system. The video content reconstruction is based on the detailed timestamped breakdown provided by the user, supplemented with web research that confirmed the video's structure, topics, and key concepts. No content was fabricated. Where information could not be verified independently, it is presented as attributed to the user's summary.

**Sources consulted:**
- [AI Automation Society - Skool](https://www.skool.com/ai-automation-society)
- [Master 95% of Claude Code - Skool Post](https://www.skool.com/ai-automation-society/new-video-master-95-of-claude-code-in-36-mins-as-a-beginner)
- [Claude Code Official Documentation](https://code.claude.com/docs/en/quickstart)
- [GitHub: Joseph19820124/Claude-20250520-nateherk](https://github.com/Joseph19820124/Claude-20250520-nateherk)
- [Nate Herk Official Site](https://nateherk.com)
