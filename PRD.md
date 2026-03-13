# PRD: External-Experience AI QA Agent
**Working name:** HumanLens QA  
**Purpose:** Build an open-source QA system that evaluates a shipped product like real users would, across web and mobile, without inspecting code, and produces evidence-backed findings plus repair briefs for coding agents such as Claude Code or Codex.

---

## 1. Product Summary

### 1.1 Objective
Create an AI QA system that:
- understands what a product is meant to do
- generates a team of targeted user agents to evaluate it from realistic user perspectives
- runs product evaluation through UI only, on web and mobile
- uses common sense, specialist lenses, and institutional/governance review where relevant
- identifies functional, UX, UI, trust, performance, provenance, auditability, and governance issues
- outputs structured, evidence-backed findings that humans and coding LLMs can act on immediately

### 1.2 Core Principle
This product is **not** a code reviewer. It must **not inspect source code, architecture, repo files, or internal implementation** to judge quality. It evaluates the product strictly through the **observable user experience**.

### 1.3 Success Definition
A successful run should, with minimal setup:
- infer what the product is for
- identify the right user and institutional perspectives to test from
- exercise critical flows on web and mobile
- detect meaningful issues using common sense, not just brittle assertions
- produce a clear prioritised report with screenshots, traces, logs, repro steps, and fix-oriented summaries

---

## 2. Product Goals

### 2.1 Primary Goals
- Evaluate products as if real humans were using them on desktop, mobile web, or mobile apps
- Use multiple agent personas, not a single generic tester
- Judge quality from the outside, including whether something technically works but still feels broken, confusing, or untrustworthy
- Support institutional-quality review where products require provenance, verifiability, audit trail, and governance
- Produce reports that are immediately usable by Claude Code, Codex, or engineers

### 2.2 Non-Goals
- Static code review
- Internal architecture analysis
- Source-level debugging
- Replacing developer test suites
- Deep compliance certification
- Full device-lab infrastructure in v1

---

## 3. Users

### 3.1 Primary Users
- solo builders
- startup product teams
- AI product teams
- enterprise/internal tool builders
- designers and PMs who need outside-in QA
- engineers using Claude Code or Codex for implementation and repair

### 3.2 Secondary Users
- QA leads
- design reviewers
- founders
- enterprise buyers evaluating product maturity
- institutional teams needing trust/governance review

---

## 4. Core User Story
> As a builder, I want to point the system at my product and have it behave like a team of realistic users and specialist reviewers, so I get an outside-in assessment of what is broken, confusing, slow, untrustworthy, or institutionally weak, with evidence and clear handoff for implementation fixes.

---

## 5. Functional Requirements

## 5.1 Invocation and Inputs
The system must accept:
- product URL and/or mobile app target
- credentials or seeded test accounts where needed
- optional product brief
- optional user personas or target audience hints
- optional critical flows to prioritise
- optional design system or brand guidance
- optional specialist review toggles
- optional institutional review toggle, though the system should infer relevance itself

---

## 5.2 Product Intent Modeling
Before testing, the system must build a **Product Intent Model** from visible product surfaces and provided context.

### It must infer:
- product type
- target audience
- primary jobs to be done
- likely user expectations
- critical journeys
- trust-sensitive or high-risk actions
- whether institutional/governance review is relevant

### Sources allowed:
- landing page
- onboarding flow
- help docs / FAQs
- app store description
- visible UI copy
- user-supplied brief
- external product/category context where necessary

### Constraint
This stage must not rely on code inspection.

### Output
A structured Product Intent Model with:
- inferred product purpose
- user hypotheses
- key journeys
- assumptions
- confidence level

---

## 5.3 Dynamic Agent Generation
The system must generate a tailored team of user agents based on the Product Intent Model.

### Each agent must have:
- name / label
- role or persona type
- goals
- expectations
- patience/friction tolerance
- expertise level
- likely behavioural style
- device/platform preference where relevant

### Agent types may include:
- first-time user
- high-intent user
- power user
- skeptical buyer
- distracted mobile user
- trust-sensitive user
- accessibility-sensitive user
- design-sensitive user
- edge-case explorer
- admin/operator
- professional/institutional user
- manager/decision-maker
- risk/compliance reviewer
- audit/oversight reviewer
- procurement/enterprise buyer

### Requirement
Personas must be generated dynamically from product context, not chosen from a static generic list.

---

## 5.4 Agent Team Orchestration
The system must coordinate agents as a team.

### It must:
- assign different goals across agents
- minimise redundant exploration
- maintain a shared coverage map
- support parallel or sequential runs
- compare findings across agent perspectives
- detect where multiple agents converge on the same issue

### Coverage map must track:
- visited screens/states
- attempted flows
- unvisited high-priority paths
- failures
- inconsistent outcomes
- repeated friction points

---

## 5.5 External-Experience Product Evaluation
The system must evaluate the product through UI interaction only.

### Allowed interaction modes:
- click
- tap
- type
- scroll
- navigate
- upload where relevant
- switch views
- wait for results
- inspect visible elements
- observe performance and timing
- capture screenshots/videos/logs/traces

### Evaluation dimensions
The system must evaluate:

#### Functional quality
- links
- buttons
- forms
- search
- filters
- navigation
- state changes
- error handling
- edge-case outcomes

#### UX quality
- clarity
- discoverability
- friction
- onboarding quality
- task completion ease
- recovery from mistakes
- information architecture
- confidence during use

#### UI quality
- spacing/alignment
- hierarchy
- consistency
- responsiveness
- visual coherence
- mobile ergonomics
- component state quality

#### Performance quality
- page/screen load
- interaction latency
- hanging or jank
- retries/timeouts
- perceived speed

#### Trust and engagement quality
- credibility
- confidence in outputs
- onboarding motivation
- copy quality
- whether the product feels safe and sensible to use

---

## 5.6 Common-Sense Judgment
The system must explicitly apply common sense, not just mechanical checks.

### It must ask and answer questions such as:
- Is the next step obvious?
- Does this behave as a normal user would expect?
- Is the UI technically functional but practically useless?
- Would a user trust this?
- Would a user give up here?
- Is the copy confusing or misleading?
- Does the product ask too much effort for too little value?
- Does this feel broken even without a visible error?
- Is this acceptable on a phone in real-world use?

### Reporting rule
Findings must separate:
- observed facts
- inferred usability judgment
- hypotheses

---

## 5.7 Specialist Lenses and External APIs
The system must support specialist review layers through external APIs or modules operating on user-visible artifacts and observed behaviour.

### Initial specialist lenses
- design critique
- accessibility review
- performance review
- copy/tone review
- trust/safety review where relevant

### Design lens must assess
- hierarchy
- spacing/alignment
- readability
- CTA prominence
- visual polish
- consistency
- brand coherence

### Constraint
Specialist modules must not require source-code inspection.

---

## 5.8 Institutional Mindset and Governance Review
The system must support institutional-quality evaluation when relevant to the product category.

### It must assess:
- source verification
- provenance
- data freshness visibility
- distinction between fact, inference, and generated content
- traceability of important outputs
- audit trail quality
- governance and control layers
- role separation and approvals where relevant
- whether a serious professional could trust and adopt the product

### Institutional personas may include:
- analyst/professional user
- manager/decision-maker
- risk/compliance reviewer
- audit/oversight reviewer
- enterprise buyer/procurement reviewer

### Institutional review questions
- Can important outputs be verified?
- Are sources specific enough?
- Is freshness clear where it matters?
- Could a team reconstruct what happened later?
- Are risky actions gated appropriately?
- Are there meaningful logs, versioning, or approval steps?
- Would this survive review by risk, compliance, or procurement?

### Institutional findings categories
- source/provenance issues
- data integrity issues
- auditability gaps
- governance/control gaps
- professional trust gaps

---

## 5.9 No-Code Boundary
The system must maintain a strict boundary between external-experience QA and internal code QA.

### It must not:
- inspect repos
- read source files to form product judgments
- diagnose root cause from implementation detail
- duplicate work better suited to Claude Code or Codex

### It must do:
- identify product-facing issues
- provide evidence
- describe user impact
- generate repair briefs from a product-experience perspective

---

## 5.10 Scheduling and Overnight Runs
The system must support scheduled unattended runs.

### It must:
- run on demand
- run overnight on a schedule
- preserve artifacts from each run
- compare against prior runs if baseline exists
- produce a morning summary

---

## 5.11 Reporting and Handoff
The system must produce outputs for both humans and coding agents.

### Final report must include:
- product understanding summary
- agent team summary
- prioritised findings
- evidence pack
- platform-specific findings
- institutional-readiness section where relevant
- suggested fixes from a product perspective
- machine-readable issue export

### Each issue must include:
- title
- severity
- confidence
- platform
- category
- user impact
- repro steps
- expected vs actual
- screenshots/videos/traces/logs
- observed facts
- inferred judgment
- hypotheses
- likely product area
- fix brief for coding agents

---

## 6. User Experience Requirements

## 6.1 Setup UX
The system should require very little setup:
- target URL or app target
- credentials if needed
- optional testing focus
- optional run schedule

## 6.2 Run UX
The system should feel like invoking an evaluation team, not configuring a brittle test framework.

## 6.3 Report UX
The report must be readable by:
- product manager
- designer
- engineer
- coding LLM

It must prioritise signal over noise.

---

## 7. Outputs

## 7.1 Human Report
Markdown/HTML report containing:
- executive summary
- what product the system thinks this is
- who it tested as
- what worked
- what failed
- what feels broken/confusing/untrustworthy
- institutional-readiness review where applicable
- top improvements

## 7.2 Machine Output
JSON export containing:
- run metadata
- product intent model
- agent definitions
- issue objects
- evidence paths
- scores and confidence

## 7.3 Coding-Agent Handoff
Per-issue repair brief designed for Claude Code or Codex:
- concise issue statement
- user impact
- repro steps
- evidence links
- likely area to inspect
- regression test suggestion

---

## 8. Prioritisation

# Must-Have for Immediate Build
These are required in the first implementation. No hiding behind “future roadmap” fog.

### A. Core system
- product intent modeling
- dynamic persona generation
- agent orchestration
- web evaluation via UI
- mobile evaluation for at least one critical flow
- common-sense issue detection
- evidence capture
- structured reporting
- scheduling/night run support
- coding-agent handoff

### B. Evaluation dimensions
- functional review
- UX review
- UI review
- performance observations
- trust/engagement review

### C. Specialist review
- design lens in initial release

### D. Institutional lens
- institutional relevance detection
- at least one institutional review path
- provenance / auditability / governance review in final report

### E. Constraints
- no source-code inspection
- open-source architecture
- runnable by Claude Code or Codex with minimal ambiguity

---

# Should-Have for Day 2 Build
These should be built immediately after the core version is working.

### A. More specialist lenses
- accessibility review
- copy/tone review
- deeper performance analysis

### B. Broader agent sophistication
- better behavioural variance
- interruption/distraction simulation
- stronger cross-agent comparison

### C. Reporting improvements
- trend comparison vs prior runs
- issue clustering/deduplication refinement
- scorecards by category

### D. Platform expansion
- deeper native mobile flows
- stronger parity checks between web and mobile

### E. Integrations
- GitHub issue export
- Slack summary
- Jira/Linear export later

---

# Won’t-Have for Initial Build
- source-code review
- full device farm
- formal compliance certification
- advanced enterprise RBAC integration
- autonomous bug fixing
- deep internal observability integrations
- polished dashboard before core quality works

---

## 9. Recommended Build Approach for Claude Code / Codex

## 9.1 Architecture Principles
- keep the click/tap execution layer deterministic
- let LLMs interpret product intent, generate personas, apply common sense, and synthesise findings
- keep evidence first-class
- maintain a strict no-code-inspection boundary
- make outputs structured and composable

## 9.2 Suggested Components
- **Intent Modeler**
- **Persona Generator**
- **Run Planner**
- **Web Runner**
- **Mobile Runner**
- **Design Review Module**
- **Institutional Review Module**
- **Evidence Collector**
- **Issue Synthesizer**
- **Report Generator**
- **Scheduler**

## 9.3 Suggested Stack
- Python for orchestration and LLM workflows
- FastAPI for API/service layer
- Playwright for web execution
- Maestro for mobile execution
- simple scheduler first, not workflow-opera nonsense
- JSON + Markdown outputs
- local/artifact storage for screenshots, traces, and logs

---

## 10. Execution Flow

### Step 1
Ingest inputs and target product.

### Step 2
Build Product Intent Model from visible product surfaces and user-provided context.

### Step 3
Determine if institutional/governance review is required and at what intensity.

### Step 4
Generate a team of relevant user and institutional agents.

### Step 5
Plan journeys and assign them across agents.

### Step 6
Execute web and mobile evaluation via UI interactions only.

### Step 7
Apply specialist review layers on captured artifacts.

### Step 8
Aggregate evidence and findings across agents.

### Step 9
Rank, deduplicate, and structure issues.

### Step 10
Produce human report, machine output, and coding-agent handoff briefs.

---

## 11. Acceptance Criteria

The initial build is successful if it can:

1. infer a reasonable product purpose from the visible product
2. generate relevant user agents without manual hardcoding
3. run at least one meaningful web evaluation end-to-end
4. run at least one meaningful mobile critical-path evaluation
5. detect functional and usability issues with evidence
6. include common-sense judgments separated from raw observations
7. apply a design lens
8. apply an institutional/provenance/governance lens where relevant
9. produce structured issue outputs suitable for Claude Code or Codex
10. run unattended overnight and output a usable morning report

---

## 12. Example Issue Schema

```json
{
  "id": "ISS-001",
  "title": "Portfolio summary appears authoritative but has no source trail",
  "severity": "high",
  "confidence": 0.9,
  "platform": "web",
  "category": "institutional_trust",
  "agent": "risk_compliance_reviewer",
  "user_impact": "A professional user cannot verify the basis of the output and may not trust it for decision-making.",
  "repro_steps": [
    "Login",
    "Open portfolio insights",
    "Read generated summary",
    "Attempt to view source basis or timestamp"
  ],
  "expected": "Key output should show traceable supporting records, source references, and freshness markers.",
  "actual": "Summary presents conclusions with no visible sources, timestamps, or provenance.",
  "observed_facts": [
    "No source links or references were visible",
    "No freshness timestamp was shown",
    "No audit/history view was available from the summary screen"
  ],
  "inferred_judgment": "The product may be acceptable for casual use but is not trustworthy enough for institutional decision support.",
  "hypotheses": [
    "Provenance may not be exposed in UI",
    "Governance model may be incomplete for professional workflows"
  ],
  "evidence": {
    "screenshots": ["artifacts/iss-001-screen-1.png"],
    "trace": "artifacts/iss-001-trace.zip",
    "logs": ["artifacts/run-console.log"]
  },
  "likely_product_area": "insights_summary_ui",
  "repair_brief": "Expose source references, freshness markers, and an audit/history entry point for generated summaries."
}
```

---

## 13. Build Notes for the Implementing Coding Agent

### Implementation constraints
- do not add any code-analysis features
- do not assume internal repo access is part of runtime QA
- optimise for working end-to-end flow, not architecture vanity
- prefer modularity over cleverness
- prioritise evidence capture and report quality
- keep prompts and schemas explicit and inspectable

### Build order
1. intent modeler
2. persona generator
3. web runner
4. issue schema + report generator
5. scheduler
6. mobile critical path
7. design lens
8. institutional lens
9. day-2 enhancements

---

## 14. One-Paragraph Build Brief for Claude Code / Codex

Build an open-source external-experience AI QA system that understands a product’s likely purpose from visible surfaces, generates a team of realistic user and institutional personas, evaluates the product strictly through web/mobile UI interactions without inspecting code, applies common-sense, design, and governance/provenance judgment, captures evidence, and outputs prioritised issue reports plus structured repair briefs for coding agents. The initial build must include all core functions immediately, with day-2 additions for deeper specialist review, better issue synthesis, and broader platform depth.
