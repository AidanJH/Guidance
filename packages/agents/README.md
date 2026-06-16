# guidance-agents

PocketFlow-based agent flows for the Guidance platform.

## Layout

- `src/agent_shared/` — shared agent infrastructure (prompts, LLM client, services like the MongoDB/Beanie database layer, tools).
- `src/flows/` — concrete agent flows (`task_assign`, `task_decomposition`), each exposing `nodes.py`, `flow.py`, and a runnable `main.py`.

Data models are imported from the `shared-contracts` package (`from shared_contracts import Task, ...`).

## Running a flow

```bash
poetry install
poetry run python -m flows.task_decomposition.main
poetry run python -m flows.task_assign.main
```
