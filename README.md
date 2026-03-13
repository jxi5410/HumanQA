# HumanQA

External-experience AI QA system. Evaluates shipped products like real users would — through the UI only, no code inspection — and produces evidence-backed findings plus repair briefs for coding agents (Claude Code, Codex).

## What It Does

1. **Understands your product** — infers purpose, audience, and critical flows from visible surfaces
2. **Generates realistic test personas** — dynamically creates a team of user agents tailored to your product
3. **Evaluates through the UI** — runs web (Playwright) and mobile (Maestro) interactions as real users would
4. **Applies specialist lenses** — design critique, institutional/governance review, trust assessment
5. **Produces actionable reports** — prioritized issues with screenshots, repro steps, and repair briefs for coding agents

## Quick Start

```bash
# Install
pip install -e ".[dev]"
playwright install chromium

# Run against a URL
humanqa run https://your-product.com

# With options
humanqa run https://your-product.com \
  --brief "B2B SaaS dashboard for financial analytics" \
  --credentials '{"email": "test@example.com", "password": "test123"}' \
  --focus "onboarding,search,export" \
  --output ./my-report

# Schedule overnight runs
humanqa schedule https://your-product.com --cron "0 2 * * *"
```

## Configuration

Create `humanqa.yaml` or pass options via CLI:

```yaml
target:
  url: https://your-product.com
  credentials:
    email: test@example.com
    password: test123

options:
  brief: "Financial analytics dashboard"
  focus_flows:
    - onboarding
    - search
    - export
  personas_hint: "enterprise finance users"
  institutional_review: auto  # auto | on | off
  design_review: true
  
llm:
  provider: anthropic  # anthropic | openai
  model: claude-sonnet-4-20250514
  api_key_env: ANTHROPIC_API_KEY

output:
  dir: ./reports
  formats:
    - markdown
    - json
    - repair_briefs
```

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-...    # Required (or OPENAI_API_KEY)
HUMANQA_OUTPUT_DIR=./reports # Optional, default: ./artifacts
```

## Architecture

```
humanqa/
├── core/
│   ├── intent_modeler.py    # Infers product purpose from visible surfaces
│   ├── persona_generator.py # Generates tailored user agent team
│   ├── orchestrator.py      # Coordinates agent runs, coverage map
│   ├── schemas.py           # All data models (issues, agents, intent)
│   └── llm.py               # LLM abstraction layer
├── runners/
│   ├── web_runner.py        # Playwright-based web evaluation
│   └── mobile_runner.py     # Maestro-based mobile evaluation
├── lenses/
│   ├── design_lens.py       # Design critique specialist
│   └── institutional_lens.py # Governance/provenance review
├── reporting/
│   ├── report_generator.py  # Human-readable reports
│   ├── machine_output.py    # JSON export
│   └── repair_briefs.py     # Coding-agent handoff
└── scheduling/
    └── scheduler.py         # Cron-based overnight runs
```

## Core Principle

This system **never inspects source code**. All evaluation happens through the observable user experience — the same surface real users see.

## Output

Each run produces:
- `report.md` — Human-readable prioritized findings
- `report.json` — Machine-readable full export
- `repair_briefs/` — Per-issue handoff files for Claude Code / Codex
- `artifacts/` — Screenshots, traces, logs

## License

MIT
