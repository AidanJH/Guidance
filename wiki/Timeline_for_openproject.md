# Guidance — 4-Month Development Timeline
**Start date:** Week of April 21, 2026
**Target completion:** Week of August 17, 2026
**Assumption:** ~15-20 hours/week (evenings + weekends, working full-time)

## Current State
- `guidance/` directory: empty (this is where the real app lives)
- `guidance-deep-research/`: tutorial/prototype code — reusable pieces include:
  - LLM client (`utils.py`) pointing at kobold.cpp on `192.168.50.50:5002`
  - Prompt versioning system (`prompts/__init__.py`) with Langfuse sync + Jinja templating
  - PocketFlow node/flow patterns (`nodes.py`, `flow.py`)
  - Flow visualization (`pocketflow-visualization/`)
- Infrastructure running: kobold.cpp (Gemma 4, 6GB VRAM), Langfuse (tracing + prompt versioning)
- Python 3.12, Poetry for dependency management
- OpenProject for ticket tracking

## Key Milestones
1. **End of Month 1 (May 18):** Working CLI — input a task, get decomposed subtasks with inferred attributes, stored in a database
2. **End of Month 2 (June 15):** End-to-end flow — tasks get scheduled into a calendar, evaluation pipeline producing quantitative results
3. **End of Month 3 (July 13):** Fine-tuned model evaluated against base model, basic web UI for task input and calendar view
4. **End of Month 4 (August 17):** Containerised, documented, demo-ready. Job applications actively in progress.

---

# Month 1: Core Pipeline (Weeks 1-4)
**Goal:** A CLI where you type a task, the LLM decomposes it, infers attributes, and stores structured results in a database.

## Week 1 (April 21-27): Project Scaffold + Data Model
This week is about setting up the real project structure and defining how tasks are stored.

### Tasks
- Create the `guidance/` project structure:
  ```
  guidance/
    pyproject.toml
    src/
      guidance/
        __init__.py
        main.py              # CLI entry point
        config.py             # App configuration (LLM endpoint, DB path, etc.)
        models/
          __init__.py
          task.py             # Task data model (dataclass/Pydantic)
        db/
          __init__.py
          repository.py       # Data access interface (abstract)
          sqlite_repo.py      # SQLite implementation
          migrations/
            001_initial.sql
        llm/
          __init__.py
          client.py           # LLM client (ported from utils.py)
          prompts/
            __init__.py        # Prompt versioning (ported from tutorial)
        flows/
          __init__.py
        utils/
          __init__.py
    tests/
      __init__.py
  ```
- Define the Task data model with the minimum scheduler attributes agreed in Brainstorming.md:
  - `id` (UUID)
  - `display_text` (str)
  - `estimated_duration_minutes` (int or range)
  - `priority` (enum: critical/high/medium/low)
  - `priority_reasoning` (str — why this priority was inferred)
  - `dependencies` (list of task IDs)
  - `related_tasks` (list of task IDs)
  - `goal_id` (optional, links to parent goal)
  - `recurring` (optional recurrence rule)
  - `hard_deadline` (optional datetime)
  - `category` (enum: health/social/professional/personal/financial)
  - `category_reasoning` (str)
  - `status` (enum: pending/scheduled/in_progress/completed/deferred)
  - `created_at`, `updated_at` (datetime)
  - `source_input` (str — the original user text that generated this task)
- Define a Goal model (lightweight — just `id`, `display_text`, `category`, `created_at`)
- Implement SQLite repository with basic CRUD: create_task, get_task, list_tasks, update_task
- Write the initial migration SQL
- Port the LLM client from `guidance-deep-research/src/guidance_task_decomposition/utils.py`
- Port the prompt versioning system from `guidance-deep-research/src/guidance_task_decomposition/prompts/__init__.py`
- Set up the config system (read from `.env` or config file: LLM endpoint, Langfuse keys, DB path)

### Deliverable
`poetry run python -m guidance.main` starts, connects to the LLM, and can create/read tasks in SQLite. No intelligence yet — just the skeleton.

### Validation
- Unit tests for Task model serialization/deserialization
- Unit tests for SQLite repository CRUD operations
- LLM client can successfully call kobold.cpp and get a response

---

## Week 2 (April 28 - May 4): Task Decomposition Flow
This week builds the core LLM pipeline: user input → decomposed subtasks with inferred attributes.

### Tasks
- Write the task decomposition prompt (Jinja template). This is the most important prompt in the system. It should:
  - Accept: the user's raw input, existing goals (if any), and user context summary
  - Output: a structured list of subtasks, each with all inferred attributes + reasoning
  - Specify the output format (start with YAML, since your tutorial already uses this)
  - Include few-shot examples in the prompt for output consistency
- Register the prompt in `prompts.yaml` for Langfuse versioning
- Implement PocketFlow nodes:
  - `TaskIntakeNode`: receives user input from CLI, loads existing goals/context from DB
  - `DecompositionNode`: calls LLM with the decomposition prompt, parses structured output
  - `OutputParserNode`: validates the LLM output against the Task model schema, handles malformed responses (retry logic)
- Wire nodes into a `task_intake_flow` using PocketFlow
- Implement basic CLI interaction: prompt user for input → run flow → display results
- Handle the common failure mode: LLM returns malformed YAML. Implement retry with error feedback (tell the LLM what was wrong and ask it to try again).

### Deliverable
You can type "I want to eat healthy" into the CLI and get back a list of subtasks with durations, priorities, categories, and reasoning — all parsed into Task model objects and printed to the console.

### Validation
- Run 5 different task inputs manually and inspect the outputs for quality
- Verify Langfuse shows traces for each decomposition call
- Verify prompt version is tracked in `prompts.yaml`

---

## Week 3 (May 5-11): Clarifying Questions + User Review
This week adds the interactive loop: the LLM asks what it can't infer, and the user can approve/edit.

### Tasks
- Write a clarifying questions prompt template. This prompt receives:
  - The decomposed subtasks with their inferred attributes
  - A list of attributes that had low inference confidence
  - Instructions to generate only targeted, non-overwhelming questions (max 3)
- Implement PocketFlow nodes:
  - `ClarificationNode`: reviews decomposition output, calls LLM to identify gaps, generates questions
  - `UserReviewNode`: displays subtasks + reasoning + clarifying questions to user via CLI, accepts edits
- Add an `inference_confidence` field to each inferred attribute (high/medium/low) — the LLM self-reports this
- Implement the review CLI interface:
  - Display each subtask with its attributes and reasoning
  - Display clarifying questions
  - Allow the user to: approve all, edit individual attributes, answer questions, reject and re-decompose
- After user approval, persist tasks to SQLite via the repository
- Update the flow: `TaskIntakeNode` → `DecompositionNode` → `OutputParserNode` → `ClarificationNode` → `UserReviewNode` → persist to DB

### Deliverable
Full interactive CLI flow: input → decomposition → clarifying questions → user review → tasks saved to database.

### Validation
- End-to-end test: input a task, answer questions, approve, verify tasks exist in SQLite
- Test the rejection path: reject decomposition, verify it re-runs
- Test editing: change a priority, verify the edited value is what gets persisted

---

## Week 4 (May 12-18): Evaluation Benchmark v1
This week builds the evaluation infrastructure that will drive all future improvement.

### Tasks
- Create a benchmark dataset: `tests/benchmarks/task_decomposition/`
  - Write 20 task inputs covering different life domains:
    - 5 health-related (e.g., "I want to run a marathon", "I need to lose 10kg")
    - 5 professional (e.g., "I want to get an AI engineering job", "Learn Kubernetes")
    - 5 personal (e.g., "I want to read 20 books this year", "Renovate the bathroom")
    - 5 mixed/complex (e.g., "I want to eat healthy while saving money", "Plan a trip to Japan while studying for a cert")
  - For each input, write a "gold standard" decomposition: the ideal subtasks with ideal attributes. This is manual and tedious but essential.
  - Store as YAML or JSON files: `input.yaml` + `expected_output.yaml` per test case
- Define evaluation metrics:
  - **Subtask completeness**: did the LLM identify all the key subtasks? (recall against gold standard)
  - **Attribute accuracy**: for each subtask, how well do inferred attributes match the gold standard? (priority match, category match, duration within ±30%)
  - **Output validity**: did the LLM produce parseable, schema-valid output? (binary)
  - **Reasoning quality**: does the reasoning string actually justify the inferred value? (manual scoring for now, 1-5 scale)
- Build an evaluation runner script (`tests/eval_runner.py`):
  - Loads all benchmark cases
  - Runs the decomposition flow on each
  - Computes metrics
  - Outputs a summary report (text + JSON)
  - Logs all runs to Langfuse with eval metadata tags
- Run the first benchmark. Record the baseline scores. This is your "v1" number.
- Commit the baseline results to the repo (e.g., `tests/benchmarks/results/baseline_v1.json`)

### Deliverable
A command like `poetry run python -m tests.eval_runner` that runs 20 test cases, produces a scored report, and logs everything to Langfuse. You know your system's baseline accuracy.

### Validation
- Benchmark runs end-to-end without crashing
- Results are logged in Langfuse with correct tags
- You have a concrete baseline number for each metric (even if the numbers are bad — that's expected)

---

# Month 2: Scheduling + Iteration (Weeks 5-8)
**Goal:** Tasks get placed into a calendar. Evaluation drives prompt improvements with measured results.

## Week 5 (May 19-25): Calendar Data Model + Deterministic Scheduler
This week builds the scheduling engine — no LLM involved, pure algorithms.

### Tasks
- Extend the data model:
  - `CalendarEvent` model: `id`, `title`, `start_time`, `end_time`, `is_fixed` (user-set appointments vs. scheduled tasks), `task_id` (optional link to a Task), `recurrence_rule`
  - `ScheduleSlot` model: represents an available time block
  - Add calendar-related tables to SQLite, write migration
- Implement schedule generation:
  - `AvailabilityCalculator`: given existing calendar events + user preferences (working hours, sleep, blocked times), compute available time slots for a date range
  - `TaskPlacer`: given a list of tasks with priorities, durations, deadlines, and dependencies + available slots, place tasks into the calendar using a priority queue approach:
    1. Sort tasks by: hard deadline (soonest first) → priority (highest first) → dependencies (dependents last)
    2. For each task, find the first available slot that fits the duration
    3. Respect dependencies: don't schedule a task before its dependencies are scheduled
    4. If a task doesn't fit anywhere, flag it as "unschedulable" with a reason
- Implement user preference storage:
  - Working hours (e.g., 9am-5pm weekdays, flexible weekends)
  - Sleep hours
  - Blocked recurring times (e.g., gym MWF 6-7am)
  - Store in SQLite as a simple key-value config table for now

### Deliverable
Given a set of tasks in the DB and user preferences, the scheduler produces a week's calendar with tasks placed in available slots.

### Validation
- Unit tests: scheduler respects dependencies (B depends on A → A is scheduled before B)
- Unit tests: scheduler respects deadlines (task with Friday deadline isn't placed on Saturday)
- Unit tests: scheduler doesn't double-book time slots
- Unit tests: high priority tasks get earlier slots than low priority tasks

---

## Week 6 (June 1-7): End-to-End Integration
This week connects the LLM pipeline to the scheduler — the full flow from input to calendar.

### Tasks
- Implement a `SchedulingNode` (PocketFlow) that:
  - Takes approved tasks from the user review step
  - Calls the `TaskPlacer` to schedule them against existing calendar state
  - Returns the proposed schedule
- Implement a `ScheduleReviewNode`:
  - Displays the proposed week view to the user in CLI (text-based calendar grid)
  - Allows the user to accept, reject, or manually adjust placements
  - On accept, persists calendar events to SQLite
- Build a "week view" CLI command: `guidance schedule show` — prints current week's scheduled tasks and events
- Build a "task list" CLI command: `guidance tasks list` — shows all tasks with statuses
- Wire the complete flow:
  `TaskIntakeNode` → `DecompositionNode` → `OutputParserNode` → `ClarificationNode` → `UserReviewNode` → `SchedulingNode` → `ScheduleReviewNode` → persist
- Add a separate flow for viewing/managing the schedule (not every interaction is task creation)

### Deliverable
Complete CLI app: `guidance add "I want to eat healthy"` → decomposition → review → scheduling → see it on your calendar via `guidance schedule show`. This is the MVP.

### Validation
- Full end-to-end manual test: add a task, see it scheduled, add another task, verify it fits around the first
- Add a task with a deadline, verify it's placed before the deadline
- Add a high-priority task to a full week, verify it displaces lower-priority tasks or gets flagged

---

## Week 7 (June 8-14): Prompt Iteration Driven by Evals
This week is dedicated to improving the system's quality using the evaluation pipeline.

### Tasks
- Run the full benchmark from Week 4 again (now with the integrated system, not just decomposition)
- Analyse the results: where is the LLM failing?
  - Common failure modes to look for:
    - Duration estimates wildly off (too optimistic or too pessimistic)
    - Missing obvious subtasks
    - Wrong category assignments
    - Vague or circular reasoning ("priority is high because it's important")
    - Malformed output requiring retries
- For each failure pattern, iterate on the prompt:
  - Add/refine few-shot examples targeting the failure mode
  - Adjust instruction clarity for attributes the LLM gets wrong
  - Experiment with output format changes if parsing is fragile
  - Try adjusting temperature and other generation parameters
- After each prompt change:
  - Re-run the benchmark
  - Record the delta in each metric
  - Commit the results with the prompt version number
  - Verify improvement in Langfuse traces
- Target: achieve measurable improvement on at least 2 metrics vs. the Week 4 baseline
- Document what worked and what didn't in a `docs/eval_log.md`

### Deliverable
At least 3 prompt iterations with measured results. A documented eval log showing: "v1 scored X, v2 scored Y after changing Z, v3 scored W after changing Q." This is the portfolio evidence of eval-driven development.

### Validation
- `docs/eval_log.md` contains at least 3 entries with quantitative before/after comparisons
- Langfuse shows distinct prompt versions with associated trace quality
- At least one metric has improved by >10% from baseline

---

## Week 8 (June 15-21): Context Retrieval + Priority Comparison
This week adds the system's ability to reason about *existing* tasks when processing new ones — the key differentiator over dumb schedulers.

### Tasks
- Implement a `ContextRetrievalNode` that, given a new task input, queries the DB for:
  - All tasks in the current week
  - All tasks with the same category as the new task
  - All tasks related to the same goal
  - Any overdue or deferred tasks
  - User preferences relevant to the task's category
- Implement a `PriorityComparisonNode` that:
  - Takes the newly decomposed subtasks + the retrieved existing tasks
  - Calls the LLM with a priority comparison prompt: "Given these existing commitments and these new subtasks, rank them all by priority and explain your reasoning"
  - The LLM may suggest re-prioritising existing tasks (e.g., "meal prep should move up because you haven't done it in 2 weeks")
- Write the priority comparison prompt (Jinja template):
  - Input: new subtasks + existing tasks + user context summary
  - Output: re-ranked task list with reasoning for any priority changes
- Insert these nodes into the flow between decomposition and scheduling:
  `TaskIntake` → `Decomposition` → `OutputParser` → `ContextRetrieval` → `PriorityComparison` → `Clarification` → `UserReview` → `Scheduling` → `ScheduleReview`
- Add the priority comparison prompt to the benchmark eval (new metric: does the LLM make sensible re-prioritisation decisions?)

### Deliverable
When you add a new task, the system considers your existing schedule and can suggest re-prioritising. E.g., adding "study for Azure cert" when you already have "meal prep" overdue results in the system saying "meal prep should be done first because it's been deferred for 2 weeks."

### Validation
- Manual test: add several tasks over a few days, verify new tasks are compared against existing ones
- Verify the LLM's re-prioritisation suggestions make sense (manual review of 5+ scenarios)
- Benchmark updated with priority comparison test cases

---

# Month 3: Fine-tuning + UI (Weeks 9-12)
**Goal:** Fine-tune a model on your data, build a web UI that makes the system usable day-to-day.

## Week 9 (June 22-28): Fine-tuning Dataset Preparation
### Tasks
- Collect training data from your system's actual usage over the past 2 months:
  - All successful task decompositions (where you approved the output)
  - Manually curate: fix any decompositions that were "good enough" but not great
  - Add the gold standard benchmark cases
  - Target: 50-100 high-quality input/output pairs
- Format the dataset for fine-tuning:
  - Convert to instruction-following format (system prompt + user input + ideal assistant response)
  - Split: 80% train, 20% validation
  - Store in `data/finetune/train.jsonl` and `data/finetune/val.jsonl`
- Research and select fine-tuning tooling:
  - Unsloth (fastest, supports LoRA, works with limited VRAM) — recommended starting point
  - Axolotl (more flexible, steeper setup)
  - Document the choice and reasoning
- Set up the fine-tuning environment on your server (or locally if VRAM allows with quantisation)

### Deliverable
A clean, curated training dataset ready for fine-tuning. Fine-tuning environment set up and tested with a dummy run.

### Validation
- Dataset passes format validation (valid JSONL, all required fields present)
- Dummy fine-tuning run completes without errors (even if only 1 epoch on 5 examples)

---

## Week 10 (June 29 - July 5): LoRA Fine-tuning + Evaluation
### Tasks
- Run LoRA fine-tuning on the full dataset:
  - Start with conservative hyperparameters (low rank, low learning rate)
  - Monitor training loss, watch for overfitting on the small dataset
  - Save checkpoints
- Load the fine-tuned model into kobold.cpp (or use the fine-tuning framework's inference)
- Run the full benchmark suite against:
  - Base Gemma 4 (your existing baseline)
  - Fine-tuned Gemma 4
- Compare results across all metrics:
  - Subtask completeness
  - Attribute accuracy
  - Output validity (this should improve significantly — the model learns your exact output format)
  - Reasoning quality
- Document the results in `docs/eval_log.md`:
  - Training configuration (rank, learning rate, epochs, dataset size)
  - Before/after metrics for every benchmark case
  - Analysis: what improved, what didn't, what got worse (if anything)
- If results are poor, iterate:
  - Try different hyperparameters
  - Augment the dataset with more examples targeting failure modes
  - Try a different base model if Gemma 4 doesn't fine-tune well at this scale

### Deliverable
A fine-tuned model with documented, quantitative comparison against the base model. Even if the improvement is modest, the documented comparison is the portfolio artefact.

### Validation
- Fine-tuned model runs in inference without errors
- Benchmark comparison document exists with clear numbers
- At least output validity metric improves (the model should learn to produce clean YAML consistently)

---

## Week 11 (July 6-12): Web UI — Backend API
### Tasks
- Choose a lightweight Python web framework:
  - FastAPI recommended (async, good for streaming LLM responses, auto-generates API docs)
- Implement REST API endpoints:
  - `POST /tasks` — submit a new task (triggers the full decomposition flow)
  - `GET /tasks` — list all tasks (with filters: status, category, date range)
  - `GET /tasks/{id}` — get a specific task
  - `PATCH /tasks/{id}` — update task attributes (for user edits)
  - `GET /schedule?start={date}&end={date}` — get calendar events for a date range
  - `POST /tasks/{id}/approve` — approve a decomposed task set
  - `POST /tasks/{id}/reject` — reject and re-decompose
  - `GET /decomposition/{id}/stream` — SSE endpoint for streaming LLM decomposition output
- Implement WebSocket or SSE for the decomposition flow so the UI can show the LLM thinking in real-time (you already stream from kobold.cpp)
- Add CORS middleware for the frontend
- Wire the API to the existing PocketFlow flows and SQLite repository

### Deliverable
A running FastAPI server with all endpoints functional. Testable via the auto-generated Swagger UI at `/docs`.

### Validation
- All endpoints return correct responses (test via Swagger UI or curl)
- `POST /tasks` triggers the full decomposition flow and returns structured results
- Streaming endpoint delivers chunks as the LLM generates them

---

## Week 12 (July 13-19): Web UI — Frontend
### Tasks
- Choose a frontend framework:
  - React or Svelte (your preference — pick whichever you're faster with)
  - If you want mobile-responsive from the start, use a component library like shadcn/ui (React) or Skeleton (Svelte)
- Implement core views:
  - **Task input view**: text input field, submit button, streaming display of LLM decomposition as it generates
  - **Decomposition review view**: shows subtasks with inferred attributes + reasoning, edit controls for each attribute, approve/reject buttons, clarifying questions section
  - **Calendar/schedule view**: weekly grid showing scheduled tasks and events, colour-coded by category, click on a task to see details
  - **Task list view**: all tasks with status filters, sortable by priority/deadline/category
- Connect to the backend API
- Make it mobile-responsive (this is the "feel" — you want to be able to use it on your phone)

### Deliverable
A functional web UI where you can input tasks, review decompositions, approve them, and see your week's schedule. Doesn't need to be beautiful — needs to be usable.

### Validation
- Full flow works through the UI: input → decompose → review → approve → see on calendar
- UI is usable on mobile screen sizes (test with browser dev tools)
- Streaming decomposition output displays in real-time

---

# Month 4: Polish + Deploy + Job Hunt (Weeks 13-16)
**Goal:** Containerise everything, document it, make the repo portfolio-ready, and start applying for jobs.

## Week 13 (July 20-26): Containerisation
### Tasks
- Write Dockerfiles:
  - `Dockerfile.api` — the FastAPI backend + PocketFlow flows
  - `Dockerfile.frontend` — the web UI (build step + nginx/static serve)
  - Optionally: `Dockerfile.llm` — kobold.cpp with model (or document how to connect to an external instance)
- Write `docker-compose.yml` that brings up:
  - Backend API
  - Frontend
  - SQLite volume mount (persistent data)
  - Langfuse (use their official docker-compose as a base, or connect to your existing instance)
  - Network configuration so all services can communicate
- Ensure `.env.example` documents all required environment variables (LLM endpoint, Langfuse keys, etc.)
- Test: `docker-compose up` on a clean machine (or clean Docker environment) should bring up the full app
- Write a health check endpoint in the API (`GET /health`) that verifies DB and LLM connectivity

### Deliverable
`docker-compose up` starts the entire Guidance stack. Someone can clone your repo and have it running in minutes (assuming they have a kobold.cpp instance or compatible OpenAI API endpoint).

### Validation
- Fresh `docker-compose up` works without manual steps beyond setting `.env`
- All API endpoints work through the containerised stack
- Frontend loads and connects to the backend
- Data persists across container restarts (SQLite volume)

---

## Week 14 (July 27 - August 2): Documentation + Architecture Diagrams
### Tasks
- Write a comprehensive `README.md`:
  - Project overview and motivation (concise — link to Brainstorming.md for depth)
  - Architecture diagram (update the C4 diagram in draw.io to reflect what you actually built)
  - Quick start guide (docker-compose up)
  - Configuration reference (all env vars)
  - Screenshots/GIF of the UI in action
  - Link to Langfuse traces (if you can make a read-only dashboard)
  - Evaluation results summary with link to full eval log
- Update `docs/eval_log.md` with final benchmark numbers
- Write `ARCHITECTURE.md`:
  - System components and their responsibilities
  - Data flow diagram (user input → LLM → scheduler → calendar)
  - Data model documentation
  - Design decisions and trade-offs (why SQLite over Postgres, why PocketFlow, etc.)
  - What would change at scale
- Create a `CONTRIBUTING.md` (even if nobody contributes — it signals open-source maturity)
- Ensure code has docstrings on all public classes and functions
- Clean up any dead code, TODOs, or hardcoded values

### Deliverable
A repo that someone can understand in 10 minutes of reading the README. Architecture is documented. Eval results are presented clearly.

### Validation
- Give the README to someone who hasn't seen the project. Can they understand what it does and run it within 15 minutes?
- All links in docs work
- No secrets in the repo (audit `.env` files, check git history)

---

## Week 15 (August 3-9): Portfolio + Resume + Job Prep
### Tasks
- Update your resume/CV:
  - Add Guidance as a project with specific, quantitative achievements:
    - "Built a local-first agentic AI scheduling system using PocketFlow, Langfuse, and Gemma 4"
    - "Implemented eval-driven prompt development, improving task decomposition accuracy from X% to Y% over N iterations"
    - "LoRA fine-tuned a 9B parameter model, achieving Z% improvement in structured output consistency"
    - "Containerised full stack (FastAPI + React + SQLite + LLM) with Docker Compose"
  - Frame your Azure certs prominently
  - Frame your SWE experience as relevant to AI application development
- Write a short blog post or LinkedIn article:
  - "What I Learned Building a Local-First AI Scheduling System"
  - Cover: the architecture, the eval-driven approach, fine-tuning results, what surprised you
  - This serves as both content marketing and interview prep (you'll be asked to explain the project)
- Prepare a 5-minute demo script:
  - Open the app, input a realistic task, show the decomposition streaming in real-time
  - Show the reasoning displayed for each attribute
  - Show the calendar view with scheduled tasks
  - Show Langfuse traces — the observability story
  - Show the eval results — the quantitative improvement story
  - Practice this demo until it's smooth
- Create a target company list for Victoria (see Brainstorming.md career section):
  - Banks: CBA, ANZ, NAB, Westpac Melbourne offices
  - Consulting: Accenture, PwC, Deloitte Melbourne
  - Healthtech/fintech startups on BuiltInMelbourne
  - Any companies from current Seek/Indeed/LinkedIn listings that fit

### Deliverable
Resume updated, demo rehearsed, target company list ready, blog post published.

---

## Week 16 (August 10-17): Apply + Iterate
### Tasks
- Begin active job applications:
  - Apply to 10-15 roles in the first week (quality over quantity — tailor each application)
  - Target role titles: AI Engineer, GenAI Engineer, LLM Engineer, AI Application Developer
  - Salary filter: $90k+ AUD
  - Location filter: Melbourne / Victoria / Remote (Australia)
- For each application:
  - Tailor the cover letter to mention specific technologies in the job listing that you've used in Guidance
  - Link to the GitHub repo
  - Link to the blog post
- Continue using Guidance daily — every day you use it is more data, more fine-tuning material, and more things to talk about in interviews
- If you get interview callbacks, prepare for:
  - System design questions: you can whiteboard the Guidance architecture
  - Prompt engineering questions: you have documented iteration history
  - "Tell me about a project" questions: you have a 5-minute demo
  - Technical assessments: practice LeetCode/HackerRank lightly, but your project experience is the stronger asset for AI roles

### Deliverable
Applications submitted. Interview pipeline started. Guidance is being used daily as a real tool.

---

# Risk Mitigation

## If the LLM quality is too low (discovered in Weeks 2-4)
- Try a different model on kobold.cpp (Qwen3-8B, Llama 3.1 8B, Mistral 7B)
- Increase context with better few-shot examples before concluding the approach is broken
- If no local model works: temporarily use a cloud API (OpenRouter, Groq free tier) to validate the architecture, then return to local optimisation later
- This is the highest risk item. Validate early. If Week 2's decomposition output is unusable, stop and fix this before proceeding.

## If fine-tuning doesn't improve results (Week 10)
- Document the negative result honestly — "I fine-tuned model X on Y examples and saw no improvement, likely because Z." A well-documented negative result is still portfolio-worthy.
- Focus the narrative on the evaluation pipeline and prompt engineering instead.

## If the project takes longer than expected
- The critical portfolio items in priority order are:
  1. Working end-to-end CLI flow (Weeks 1-3) — this alone is demo-able
  2. Evaluation pipeline with results (Week 4 + 7) — this proves engineering maturity
  3. Fine-tuning with documented comparison (Weeks 9-10) — this closes the biggest skill gap
  4. Web UI (Weeks 11-12) — nice to have but CLI demo works too
  5. Containerisation (Week 13) — can be done in a day if rushed
  6. Documentation (Week 14) — minimum viable README can be written in an evening
- If you're behind, cut the UI scope first. A polished CLI with strong evals beats a pretty UI with no evaluation story.

## If you get a job offer before Month 4
- Take it. The project doesn't need to be "finished." A working MVP + documented evals + fine-tuning attempt is enough. You can continue building Guidance on evenings/weekends with real AI engineering experience to inform the design.
