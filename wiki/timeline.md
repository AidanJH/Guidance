# Guidance - Project Timeline & Overview

Local-first, LLM-powered personal scheduling and task management.

## How to paste this into OpenProject

1. Create or open the wiki page in OpenProject.
2. Click the pencil icon to edit.
3. In the editor toolbar, click the **Source code** button (looks like `</>`), or open the three-dot menu and pick **Edit as Markdown**.
4. Paste the contents of this file.
5. Save. The `##105`-style references will render as rich work-package cards with subject and type.

If you paste directly into the WYSIWYG view without switching to source mode, the literal Markdown characters will appear as text and nothing will render.

## What Guidance is

Guidance is a personal life-management system where the LLM is a first-class citizen - not the scheduler itself, but the reasoning and prioritization layer that understands the user's full context and drives a deterministic scheduling engine.

The central idea: users give loose natural-language input, and the system decomposes it, reasons about it, and schedules it - showing its work at every step.

## The problem it solves

Existing productivity tools (Motion, SkedPal, plain task lists) fail because they:

- Require excessive manual input and structuring. Friction kills adoption.
- Use context-blind algorithmic rules that don't account for the user's actual life.
- Treat AI as a bolt-on feature rather than a core architectural component.

## What the MVP delivers

A user can:

1. Type a task or goal in natural language (e.g. `I want to eat healthy`).
2. See it decomposed into atomic subtasks with inferred duration, priority, category, dependencies, and a reason for each inference.
3. Answer at most three targeted clarifying questions for what the LLM cannot infer on its own.
4. Review and edit the subtasks before anything is persisted.
5. Have approved subtasks placed into the calendar by a deterministic scheduler that respects priorities, deadlines, and dependencies.
6. Use the system from both a CLI and a mobile-responsive web UI.

## Core principles

1. **LLM as a super-powerful `if` statement**. The model reasons and prioritises; deterministic code places and persists.
2. **Minimize user friction**. Loose input, aggressive defaults, minimal questions.
3. **Show your work**. Every inferred attribute is displayed with a short reason.
4. **Modularity and swappability**. Every major component sits behind an interface.
5. **Eval-driven development**. No prompt or model change ships without a measurement.
6. **Local-first**. Runs on the user's device with a small LLM; cloud is a fallback, not a default.

## Target dates

- **Start:** Week of 21 April 2026
- **MVP complete:** Week of 17 August 2026
- **Effort budget:** 15-20 hours/week (evenings and weekends, working full-time)

## Milestones

| ID | Target week | Outcome |
| --- | --- | --- |
| M1. CLI working | 18 May 2026 | Type a task, get a structured decomposition with attributes and reasoning, stored in SQLite. |
| M2. End-to-end flow | 15 June 2026 | Tasks scheduled into a calendar; evaluation pipeline producing quantitative results. |
| M3. Fine-tune and UI | 13 July 2026 | Fine-tuned model evaluated against the base; web UI for task input and calendar. |
| M4. Ship | 17 August 2026 | Containerised, documented, demo-ready. |

## Epic map

### MVP epics

| Code | Epic | Focus |
| --- | --- | --- |
| PFN | ##105 | One-time bootstrap: project scaffold, data model, LLM client, hardware validation. |
| TDC | ##106 | Natural-language input to approved, persisted tasks with inferred attributes. |
| ISC | ##107 | Approved tasks placed into the calendar; priority comparison against existing work. |
| EVH | ##108 | Benchmark dataset and runner that drives every LLM-facing improvement. |
| MFT | ##109 | LoRA fine-tune with a measured, documented comparison against baseline. |
| UIF | ##110 | FastAPI backend and mobile-responsive web frontend. |
| REL | ##111 | Docker Compose, README, ARCHITECTURE, ADRs, diagrams. |

### Post-MVP epics (on hold)

| Code | Epic | Why deferred |
| --- | --- | --- |
| KGL | ##112 | Needs real usage traces to inform graph tech choice; MVP leaves the interface seam in place. |
| DRR | ##113 | Adds a slow and expensive call loop; base decomposition must be stable first. |
| VOI | ##114 | Adds an ASR error surface; typed-input quality should be solved first. |
| SRP | ##115 | Highest-privacy-impact feature; build after real daily use informs the design. |

## Current state

- `guidance/` directory: empty. This is where the real app will live.
- `guidance-deep-research/`: tutorial code with reusable pieces (LLM client, prompt versioning, PocketFlow patterns, flow visualization).
- Infrastructure running: kobold.cpp (Gemma 4, 6 GB VRAM), Langfuse (tracing and prompt versioning).
- Python 3.12, Poetry for dependency management.
- OpenProject for ticket tracking.

## Week-by-week plan

References like `##105` render as clickable work-package cards once this page is saved.

### Month 1: Core pipeline (Weeks 1 to 4)

Goal: a CLI where typing a task produces a decomposed, reasoned, persisted set of subtasks.

#### Week 1 (21 to 27 April): Scaffold, hardware, LLM client

- ##116 Hardware and quantization validation spike. Done first; if it fails, the project pivots before further work.
- ##64 Project scaffold and configuration.
- ##66 LLM client port and prompt versioning.

Validation: `poetry run python -m guidance.main` starts, hits the LLM, returns a response. Hardware spike result committed under `docs/spikes/`.

#### Week 2 (28 April to 4 May): Data model

- ##65 Task data model and persistence.
- ##71 Goal and task hierarchy model.
- ##72 Task relationship model.
- ##73 User profile and preferences model.
- ##70 Calendar event data model.
- ##67 Spike: data access abstraction design (must inform the above).
- ##69 Spike: prompt serialization format (feeds Week 3).

Validation: repositories round-trip all models; every mutation fires the `subscribe_to_changes` hook.

#### Week 3 (5 to 11 May): Decomposition flow

- ##76 Natural-language task decomposition.
- ##77 Attribute inference with reasoning.
- ##78 Clarifying questions.
- ##79 Task review and approval.

Validation: `guidance add "I want to eat healthy"` produces structured output, asks sensible clarifying questions, persists approved tasks.

#### Week 4 (12 to 18 May): Evaluation baseline -> M1

- ##85 Benchmark dataset (20 gold-standard cases).
- ##86 Automated evaluation runner.

Validation: `poetry run python -m guidance.eval.run` produces a scored report and a committed baseline. Langfuse shows every benchmark trace.

### Month 2: Scheduling and iteration (Weeks 5 to 8)

Goal: tasks land on a calendar; evaluation drives measured prompt improvements.

#### Week 5 (19 to 25 May): Scheduler engine

- ##80 Schedule availability calculation.
- ##81 Deterministic task scheduling.

Validation: given a set of tasks and preferences, the scheduler outputs a valid week with no double-bookings, no dependency violations, no deadline violations.

#### Week 6 (26 May to 1 June): End-to-end integration

- ##82 Schedule view.
- ##83 Schedule review and adjustment.
- ##99 Task lifecycle state-machine diagram.
- ##117 Sequence diagram: task intake flow.

Validation: `guidance add "..."` flows through decomposition, review, scheduling, then `guidance schedule show` displays the placed events. Diagrams reflect the implementation.

#### Week 7 (2 to 8 June): Prompt iteration

- ##87 Prompt iteration with measured results (at least 3 iterations).

Validation: `docs/eval_log.md` contains three entries with quantitative before-and-after comparisons. At least one metric improved by 10% or more over baseline.

#### Week 8 (9 to 15 June): Priority comparison and buffer -> M2

- ##84 Context-aware priority comparison.
- ##100 Sequence diagrams: scheduling flows.
- Buffer: any slipped work from Weeks 5 to 7 absorbed here.

Validation: adding a new task against a populated week triggers a defensible re-prioritisation suggestion. Benchmark has new priority-comparison cases.

### Month 3: Fine-tuning and UI (Weeks 9 to 13)

Goal: a fine-tuned model with documented comparison, plus a web UI usable on mobile.

#### Week 9 (16 to 22 June): Fine-tuning dataset

- ##88 Fine-tuning dataset preparation.

Validation: `train.jsonl` and `val.jsonl` committed, 80/20 split, every row passes the production schema check. Dry-run training completes.

#### Week 10 (23 to 29 June): LoRA training and evaluation

- ##89 LoRA fine-tuning and evaluation.

Validation: fine-tuned model runnable through `LLMClient`. `docs/eval_log.md` contains per-metric deltas against baseline with training curves.

#### Week 11 (30 June to 6 July): Backend API

- ##90 Backend REST API.

Validation: all endpoints testable through Swagger UI at `/docs`; `POST /tasks` triggers the full decomposition flow end-to-end; the streaming endpoint delivers chunks live.

#### Week 12 (7 to 13 July): Frontend part 1 -> M3

- ##91 Task input and decomposition view (with streaming).
- ##92 Decomposition review view.

Validation: end-to-end through the UI: input, streaming decomposition, edit, approve, persisted.

#### Week 13 (14 to 20 July): Frontend part 2

- ##93 Calendar schedule view.
- ##94 Mobile-responsive layout.

Validation: full flow usable on a 375 px phone screen. Calendar renders correctly for an empty week and a packed week.

### Month 4: Ship (Weeks 14 to 16)

Goal: containerised, documented, demo-ready.

#### Week 14 (21 to 27 July): Containerisation and architecture

- ##95 Containerisation.
- ##101 C4 architecture diagram update.
- ##97 Entity-relationship diagram.
- ##98 UML class diagram.

Validation: fresh `docker-compose up` works without manual steps beyond copying `.env`. All feature endpoints work through the containerised stack.

#### Week 15 (28 July to 3 August): Documentation

- ##96 Project documentation (README, ARCHITECTURE.md, CONTRIBUTING.md).
- ##103 Architecture decision records.
- ##104 API specification.

Validation: someone who has never seen the project can read the README and be running the app within 20 minutes. Seven ADRs cover the key design decisions.

#### Week 16 (4 to 17 August): Buffer and polish -> M4

- Absorb any slipped work.
- Final eval run against the fine-tuned model; refresh all benchmark numbers.
- Polish the demo: rehearse a 5-minute walkthrough end-to-end.
- Record a short demo GIF for the README.

Validation: the demo runs smoothly start-to-finish. The repo is ready to share.

## Risk mitigation

### If the LLM quality is too low (Weeks 2 to 4)

- Try a different model on kobold.cpp (Qwen3-8B, Llama 3.1 8B, Mistral 7B).
- Improve few-shot examples and reasoning guidance before declaring the approach broken.
- If no local model works, fall back to a cloud API (OpenRouter, Groq free tier) to validate the architecture, then return to local optimisation.
- This is the highest-risk item. The Week 1 hardware spike (##116) exists to catch it before much code is written.

### If fine-tuning does not improve results (Week 10)

- Document the negative result honestly in `docs/eval_log.md`. A well-documented negative result is still portfolio-worthy.
- Shift the narrative emphasis to the evaluation pipeline and prompt engineering iterations.

### If the project slips

Cut in this order (highest-value items kept):

1. Working end-to-end CLI flow (Weeks 1 to 3). Demo-able on its own.
2. Evaluation pipeline with real results (Weeks 4 and 7). Proves engineering maturity.
3. Fine-tuning with documented comparison (Weeks 9 to 10). Closes the biggest skill gap.
4. Web UI (Weeks 11 to 13). Nice to have; a polished CLI demo works too.
5. Containerisation (Week 14). Can be compressed to a day.
6. Documentation (Week 15). Minimum-viable README can be written in an evening.

A polished CLI plus strong evals beats a pretty UI with no evaluation story.

### If a job offer arrives before Month 4

Take it. A working MVP with documented evals and a fine-tuning attempt is sufficient. Guidance continues post-employment on evenings and weekends, now informed by real AI-engineering experience.

## Success metrics

- **Eval coverage:** 20 benchmark cases, 4 metrics, scored on every change.
- **Prompt iteration:** at least 3 measured iterations, 10% or more improvement over baseline on at least 1 metric.
- **Fine-tune:** measurable improvement on output validity vs base model, documented either way.
- **Deployment:** `docker-compose up` on a clean machine brings up the full stack.
- **Mobile usability:** the full flow is usable on a 375 px screen without horizontal scroll.
- **Documentation:** a new reader understands what the system does and runs it within 20 minutes.

## How this wiki stays current

- When a story is closed, update its week to strike through the `##id` link.
- When a week slips into the buffer, note it under that week's heading.
- When an epic finishes, tick it in the Epic map.
- If a milestone date changes, note the original and the new date side-by-side; never silently overwrite.

Keeping the wiki honest is the whole point. A timeline that lies is worse than no timeline at all.
