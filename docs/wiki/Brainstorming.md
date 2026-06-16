# Guidance — Brainstorming & Requirements

## Problem Statement

Existing productivity tools (Motion, SkedPal, plain task lists) fail because they either:

- Require excessive manual input and structuring (friction kills adoption)
- Use context-blind algorithmic rules that don't account for the user's actual life
- Treat AI as a bolt-on feature rather than a core architectural component

Guidance is a personal life management system where the LLM is the first-class citizen — not the scheduler itself, but the reasoning and prioritization layer that understands the user's full context and drives a deterministic scheduling engine.

## Core Philosophy

- **LLM as a "super powerful if statement"**: The LLM handles reasoning, prioritization, task decomposition, and context interpretation. It calls deterministic tools to actually place tasks, query data, and manage the calendar. It is not the end-to-end system.
- **Minimize user friction**: The entire point is that the user should be able to give loose, natural language input and have the system do the heavy lifting of structuring, estimating, and scheduling.
- **Show your work**: All inferred attributes (priority, duration, category, etc.) must be displayed to the user alongside a brief explanation of *why* that inference was made. This builds trust and lets the user catch mistakes early.
- **Modularity and swappability**: Every major component (data store, graph layer, LLM provider, prompt format) must be abstracted behind interfaces so that technologies can be swapped and evaluated. The right answer for most architectural choices is unknown — the system must make experimentation cheap.
- **Eval-driven development**: Langfuse for prompt tracing and versioning, plus custom evaluation harnesses, to measure the impact of changes to prompts, models, data structures, and agent workflows. Decisions should be backed by data, not assumptions.
- **Local-first**: The system must be able to run on a user's local device with a small LLM. Start with a capable foundation model, then optimise down to smaller/fine-tuned models as the system matures and we understand what each component actually needs.

## MVP Scope

The MVP proves one thing: **a user can input a task in natural language, have it decomposed into subtasks with inferred attributes, and have those subtasks scheduled into their existing calendar with LLM-driven prioritization.**

### MVP Features

1. **Task intake**: User provides a loose natural language description of a task or goal
2. **Task decomposition**: LLM breaks the input into atomic subtasks with inferred attributes
3. **Clarifying questions**: LLM asks only what it cannot resolve from existing context — without overwhelming the user
4. **User review**: Decomposed subtasks and inferred attributes are presented to the user for approval/editing
5. **Scheduling**: A deterministic scheduler places approved subtasks into the calendar, respecting existing commitments and LLM-determined priority
6. **Simple UI**: Web and mobile interfaces focused on understanding the "feel" — how the app looks and how the interaction flows — more than functional completeness

### Explicitly NOT in MVP

- Voice interface
- Screen recording / activity tracking
- Email/calendar integration with external providers
- Financial or geographical awareness
- Behavioral nudging ("pressing harder" on overdue tasks)
- Deep research on subtasks

## Architecture

### High-Level Design

```
User Input (natural language)
        │
        ▼
┌─────────────────────┐
│  Orchestrator Flow   │  (PocketFlow)
│  ┌───────────────┐   │
│  │ Task Intake    │   │  Receives user input
│  │ Node           │   │
│  └──────┬────────┘   │
│         ▼            │
│  ┌───────────────┐   │
│  │ Context        │   │  Sub-agents retrieve relevant context
│  │ Retrieval      │   │  from graph/DB, summarize, pass up
│  │ Pipeline       │   │
│  └──────┬────────┘   │
│         ▼            │
│  ┌───────────────┐   │
│  │ Decomposition  │   │  LLM decomposes task, infers attributes
│  │ + Inference    │   │
│  │ Node           │   │
│  └──────┬────────┘   │
│         ▼            │
│  ┌───────────────┐   │
│  │ Clarification  │   │  Asks user only what can't be inferred
│  │ Node           │   │
│  └──────┬────────┘   │
│         ▼            │
│  ┌───────────────┐   │
│  │ Scheduling     │   │  Deterministic scheduler places tasks
│  │ Tool           │   │
│  └───────────────┘   │
└─────────────────────┘
```

### Agent Architecture

- Built on **PocketFlow** — nodes and flows as the agent primitives
- PocketFlow flows can be pipelines, loops, or branching — use whatever topology fits the problem
- Sub-agents/nodes handle focused retrieval and summarization, feeding smaller context chunks up to the reasoning nodes
- The final reasoning LLM call receives a condensed, relevant context window — not the entire life history
- Stay close to raw API calls for visibility and debuggability

### Data Model

#### Dual-model approach

1. **Structured store** (calendar, events, task records): Traditional DB or multi-dimensional structure. Holds the canonical task data — IDs, timestamps, durations, statuses, recurrence rules. Queryable programmatically by the scheduler and UI.
2. **Knowledge graph** (LLM-accessible context): Tasks, goals, user preferences, relationships, and history represented as a graph that the LLM queries via natural language. A task exists in both the structured store (for the scheduler) and the graph (for the LLM).

#### Technology: TBD

- Start with the simplest viable option (could be as basic as SQLite + in-memory graph, or JSON files)
- Abstract behind a data access interface so the backing technology can be swapped
- Evaluate options (Neo4j, KùzuDB, custom adjacency structures, GraphRAG) against actual performance with the LLM
- Graph population strategy (single-pass vs. multi-pass, LLM-driven vs. external service) is an open experiment
- Prompt serialization format (JSON, YAML, Markdown) should also be abstracted — if a fine-tuned model works better with .md, it should be trivial to switch

#### Key principle

The data structures exist to serve the LLM's context needs efficiently. Design the graph schema around the kinds of queries the LLM will make:

- "Get me all tasks this week"
- "Get me anything related to this subtask"
- "Get me the user's preferences that are related to this task"
- "What has the user been neglecting?"

## Task Model

### Minimum attributes for the scheduler

These are the attributes a task must have for the deterministic scheduler to function:

- **ID**: Unique identifier
- **Display text**: Human-readable title/description
- **Estimated duration**: Time estimate (or range). The scheduler cannot work without this.
- **Priority**: Relative importance, influenced by urgency, user goals, and life context
- **Dependencies**: Other tasks that must complete first
- **Related tasks**: Sibling or associated tasks (not blocking, but contextually linked)
- **Overall goal relation**: Which higher-level goal this task contributes to
- **Recurring**: Whether and how this task repeats
- **Hard deadline** (optional): A fixed date/time constraint
- **Category/life domain** (inferred): Health, social, professional, personal, etc.

### Inference rules

- **Must be inferred or asked**: Estimated duration — the scheduler literally cannot place a task without this
- **Can typically be inferred**: Category/life domain, rough priority relative to existing tasks, goal relation
- **Ask only when ambiguous**: Hard deadlines, dependencies on external events, duration when the task is too novel to estimate

### Display rule

Every inferred attribute is shown to the user with a brief reason. Example:

> **Priority: High** — You haven't meal-prepped in 2 weeks and your goal is to reduce takeout spending.

## Task Intake Flow

1. User gives loose natural language input (e.g., "I want to eat healthy")
2. Context retrieval sub-agents pull relevant data: existing schedule, related goals, user preferences, recent activity
3. LLM decomposes the input into subtasks and infers attributes for each
4. LLM identifies what it cannot confidently infer and generates targeted clarifying questions
5. User is presented with: decomposed subtasks + inferred attributes with reasoning + clarifying questions
6. User approves, edits, or rejects
7. Approved subtasks are passed to the deterministic scheduler for calendar placement

## Current Infrastructure

- **LLM hosting**: kobold.cpp on personal server, currently running Gemma 4 (6GB VRAM)
- **LLM framework**: PocketFlow (lightweight, close to API calls)
- **Observability**: Langfuse (prompt versioning, tracing)
- **Project management**: OpenProject for ticket tracking
- **Architecture docs**: draw.io for C4 diagrams

## Open Questions

1. **Knowledge graph technology**: What's the right embedded graph solution for local-first? Need to evaluate options against actual LLM query patterns.
2. **Graph population strategy**: Single-pass during task decomposition, or a separate graph-building agent/service? Possibly a fine-tuned model specifically for embedding items in a knowledge graph.
3. **Context retrieval architecture**: How many sub-agent layers? What's the right granularity for retrieval vs. summarization nodes?
4. **Scheduler algorithm**: What deterministic scheduling approach? Constraint satisfaction? Priority queue with time-slot bin packing? Needs research.
5. **Prompt serialization format**: JSON vs. YAML vs. Markdown — which performs best with target models? Must be evaluated empirically.
6. **Model specialization**: As the system matures, which components can be handled by smaller/fine-tuned models vs. which need the foundation model?
7. **Evaluation harness design**: What does the custom eval framework look like beyond Langfuse? What metrics define "good scheduling"?
8. **User profile/preference modeling**: How does the system learn and maintain user preferences over time? Explicit settings vs. inferred from behavior?

## Future Features (Post-MVP)

These are validated ideas but explicitly out of scope for the MVP:

- **Automatic deep research**: Expanding subtasks by researching unknowns until accurate time estimates can be made
- **Voice interface**: Quick input via smartwatch or phone
- **Screen recording**: Desktop activity tracking (e.g., Screenpipe) for automatic progress tracking and information capture
- **External calendar/email integration**: Lower adoption friction by syncing with Google Calendar, Outlook, etc.
- **Financial/geographical awareness**: Don't suggest a certification course if the user can't afford it; factor in location for task feasibility
- **Behavioral nudging**: Escalating priority on neglected tasks, surfacing social obligations, "pressing harder" when things are overdue — requires behavioral psychology research
- **User context awareness**: Prior action tracking, on-track scoring, life pattern recognition
