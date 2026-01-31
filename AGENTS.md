# AGENTS.md

## Repository expectations

- Run `npm run lint` before opening a pull request.
- Document public utilities in `docs/` when you change behavior.

## Project structure

This repository contains the Procurement Orchestrator System for
Extrema-MG. The system uses Claude Code CLI with Skills, hooks, and
MCP servers to support public procurement management.

Key directories:

- `.claude/skills/` -- Skill definitions (SKILL.md + reference files)
- `.claude/hooks/` -- Validation hook scripts (Python)
- `sources/` -- Normative corpus and source logs (JSONL)
- `tools/` -- MCP server and API client modules (Python)
- `output/` -- Generated documents (ETP, TR, pareceres)
- `evaluations/` -- Skill evaluation test cases (JSON)
- `docs/` -- Architecture and project documentation

## Skills overview

| Skill | Purpose |
|---|---|
| price-research | Price research per IN SEGES 65/2021 |
| document-generation | Generate ETP, TR, and technical opinions |
| bid-analysis | Analyze bidding documents for compliance |
| budget-analysis | Validate budgets against SINAPI/SICRO |
| pncp-audit | Audit PNCP publications |
| normative-conflicts | Resolve normative hierarchy conflicts |
