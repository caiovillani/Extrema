#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const MAX_LINE_LENGTH = 120;
const issues = [];
const markdownFiles = [];

function walk(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === 'node_modules' || entry.name === '.git') continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath);
    } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.md')) {
      markdownFiles.push(fullPath);
    }
  }
}

function lintFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split(/\r?\n/);

  lines.forEach((line, index) => {
    const lineNumber = index + 1;
    if (line.length > MAX_LINE_LENGTH) {
      issues.push(`${filePath}:${lineNumber} Line exceeds ${MAX_LINE_LENGTH} characters.`);
    }
    if (/\s$/.test(line)) {
      issues.push(`${filePath}:${lineNumber} Trailing whitespace.`);
    }
    if (/\t/.test(line)) {
      issues.push(`${filePath}:${lineNumber} Contains tab characters.`);
    }
  });

  if (!content.endsWith('\n')) {
    issues.push(`${filePath}: Missing trailing newline at end of file.`);
  }
}

walk(process.cwd());
markdownFiles.sort().forEach(lintFile);

if (issues.length > 0) {
  console.error('Lint issues found:\n' + issues.join('\n'));
  process.exit(1);
}

console.log(`Lint passed for ${markdownFiles.length} Markdown file(s).`);
