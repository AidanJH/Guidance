# Guidance

> A local-first, LLM-powered personal scheduling and task management system.

**Status: Early development.** The core infrastructure and design is in place. Active implementation begins April 2026.

---

## What it does

You tell Guidance what you want to accomplish in plain English. It breaks your input into concrete, scheduled subtasks — showing you exactly why it made every decision — and places them into your calendar around your existing commitments.

The key difference from existing tools: the LLM is not a bolt-on feature. It is the reasoning layer. Every inferred attribute (priority, duration, category, dependencies) comes with a plain-English explanation so you can catch mistakes before anything lands on your calendar.

---

## Quick start

**Prerequisites**

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- A running [kobold.cpp](https://github.com/LostRuins/koboldcpp) instance (or any OpenAI-compatible local LLM endpoint)
- [Langfuse](https://langfuse.com/) instance for observability (self-hosted or cloud)

**Setup**

```bash
git clone https://github.com/your-username/guidance.git
cd guidance

cp .env.example .env
# Edit .env with your LLM endpoint, Langfuse keys, and DB path
```

**Install dependencies**

```bash
poetry install
```

**Run**

```bash
cd guidance/src
poetry run python main.py
```

**Add a task**

```bash
guidance add "I want to eat healthy"
```

**View your schedule**

```bash
guidance schedule show
```

---

## Environment variables

Copy `.env.example` to `.env` and fill in the values. Required variables:

| Variable | Description |
| --- | --- |
| `LLM_ENDPOINT` | Base URL of your kobold.cpp or OpenAI-compatible endpoint |
| `LLM_MODEL` | Model identifier (e.g. `gemma-4`) |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key for tracing |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key |
| `LANGFUSE_HOST` | Langfuse instance URL |
| `DB_PATH` | Path to the SQLite database file |

---

## Architecture overview

Guidance is a single-repo application with three layers that talk to each other and two external services.

```
┌─────────────────────────────────────────────────┐
│  Web UI  (React / Svelte)                       │
│  Mobile-responsive. Streams decomposition live. │
└───────────────┬─────────────────────────────────┘
                │ HTTP + SSE
┌───────────────▼─────────────────────────────────┐
│  API Service  (FastAPI)                         │
│  REST endpoints. Thin transport layer.          │
└───────────────┬─────────────────────────────────┘
                │
┌───────────────▼─────────────────────────────────┐
│  Orchestrator  (PocketFlow)                     │
│                                                 │
│  TaskIntakeNode → DecompositionNode             │
│       → ClarificationNode → UserReviewNode      │
│       → ContextRetrievalNode                    │
│       → PriorityComparisonNode                  │
│       → SchedulingNode → ScheduleReviewNode     │
└──────┬────────────────────────┬─────────────────┘
       │                        │
┌──────▼──────┐        ┌────────▼────────┐
│  LLM Client │        │  SQLite (via    │
│  (kobold.cpp│        │  Repository     │
│   endpoint) │        │  interfaces)    │
└──────┬──────┘        └─────────────────┘
       │
┌──────▼──────┐
│  Langfuse   │
│  (tracing + │
│   evals)    │
└─────────────┘
```

**Design principles:**

- **LLM as a reasoning layer, not the scheduler.** The LLM decomposes, infers, and prioritises. A deterministic algorithm places tasks.
- **Show your work.** Every inferred attribute has a short reason. Users see exactly why the system made each decision.
- **Pluggable by design.** All persistence goes through repository interfaces. The LLM provider is behind a client interface. A knowledge graph layer can slot in post-MVP without rewriting callers.
- **Eval-driven.** Every prompt change is measured against a benchmark dataset before it ships.

---

## Tech stack

| Component | Technology |
| --- | --- |
| Language | Python 3.12 |
| Package manager | Poetry |
| Agent framework | PocketFlow |
| LLM inference | kobold.cpp (local) |
| Observability | Langfuse |
| Persistence | SQLite |
| API | FastAPI |
| Frontend | React or Svelte (TBD) |

---

## Project structure

```
Guidance/
├── guidance/               # Main application (active development)
│   ├── pyproject.toml
│   └── src/
│       ├── main.py         # CLI entry point
│       ├── config.py
│       ├── models/         # Pydantic data models
│       ├── db/             # Repository interfaces + SQLite impl
│       ├── llm/            # LLM client + Jinja prompt templates
│       ├── flows/          # PocketFlow nodes and flows
│       └── utils/
├── guidance-deep-research/ # Prototype / donor code (reference only)
├── frontend/               # Web UI (added in Month 3)
├── docs/
│   ├── adr/                # Architecture Decision Records
│   ├── diagrams/           # C4, ERD, UML, sequence diagrams
│   ├── spikes/             # Spike findings and decisions
│   └── eval_log.md         # Prompt iteration results
├── tests/
│   └── benchmarks/         # Evaluation dataset and results
├── data/
│   └── finetune/           # Fine-tuning dataset (Month 3)
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── wiki/                   # OpenProject wiki drafts
└── .env.example
```

---

## Development roadmap

| Milestone | Target | Description |
| --- | --- | --- |
| M1. CLI working | 18 May 2026 | Natural-language input to decomposed, persisted tasks |
| M2. End-to-end flow | 15 June 2026 | Tasks scheduled into a calendar; eval pipeline live |
| M3. Fine-tune and UI | 13 July 2026 | LoRA fine-tuned model evaluated; web UI shipped |
| M4. Ship | 17 August 2026 | Containerised, documented, demo-ready |

See [`wiki/timeline.md`](wiki/timeline.md) for the full week-by-week breakdown with ticket references.

---

## Evaluation

Guidance uses an evaluation-driven development process. Every prompt or model change is scored against a 20-case benchmark dataset before it is considered an improvement.

```bash
poetry run python -m guidance.eval.run
```

Results are logged to Langfuse and committed to [`docs/eval_log.md`](docs/eval_log.md).

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) — coming in M4.

---

## License

MIT. See [`LICENSE`](LICENSE).
