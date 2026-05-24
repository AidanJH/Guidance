# guidance_assign

A PocketFlow agent that takes a user's goal, decomposes it into prioritised sub-tasks using an LLM, and persists the results to MongoDB.

## How it works

```
TaskAssignNode  ──"persist"──►  PersistTasksNode
  LLM call                        Save to MongoDB
  YAML parse                      tasks collection
```

**`TaskAssignNode`**
- Builds a prompt from the user's task and their context
- Streams the LLM response
- Parses the returned YAML into a `TaskDecompositionResult`
- Stores the result in shared state and transitions to `"persist"`

**`PersistTasksNode`**
- Converts each `SubTask` into a `Task` document
- Maps integer sub-task dependency IDs to the new UUID-based Task IDs
- Inserts all tasks into the `tasks` MongoDB collection
- Prints a summary of what was saved

## Running

```bash
# Start MongoDB (first time or after a restart)
docker start guidance-mongo

# Run with the default question
poetry run python src/guidance_assign/main.py

# Run with a custom task
poetry run python src/guidance_assign/main.py --"Help me get fit"
```

After it runs, verify tasks were saved:
```bash
poetry run python src/database/get_tasks.py
```

## Shared state

| Key | Set by | Description |
|---|---|---|
| `task_from_user` | caller / `main.py` | The user's original input |
| `context` | `main.py` | Background info about the user passed to the prompt |
| `decomposition_result` | `TaskAssignNode` | Parsed `TaskDecompositionResult` |
| `persisted_task_ids` | `PersistTasksNode` | List of MongoDB Task IDs that were saved |

## Prompt

Template: `prompts/task_assign.jinja`

Inputs:
- `{{ context }}` — background information about the user
- `{{ task_from_user }}` — the user's goal or request

Expected LLM output (YAML):
```yaml
Overall Task Assessment: |
  # Evaluation of User Context: ...
  # Evaluation of the task: ...
Subtasks:
  - description: "Subtask description"
    status: "Pending/Done/Further Information Needed"
    priority: "Low/Medium/High/Critical"
    id: 1
    dependencies: [list of other subtask ids this depends on]
```

## Task fields populated on save

| Field | Source |
|---|---|
| `id` | Auto-generated UUID |
| `display_text` | First 80 chars of `description` |
| `description` | Full subtask description from LLM |
| `status` | From LLM output |
| `priority` | From LLM output, defaults to `Medium` if missing |
| `source_input` | Original `task_from_user` string |
| `dependencies` | Remapped from subtask int IDs to Task UUIDs |
| `created_at` / `updated_at` | Set to current datetime on insert |

## Files

```
guidance_assign/
  main.py          — entry point, sets up shared state and runs the AsyncFlow
  flow.py          — wires TaskAssignNode → PersistTasksNode
  nodes.py         — TaskAssignNode and PersistTasksNode
  utils.py         — call_llm helper (OpenAI-compatible streaming)
  prompts/
    task_assign.jinja   — prompt template
    prompts.yaml        — prompt version manifest
  viz/
    task_assign.html    — D3 flow visualisation
    task_assign.json    — flow graph data
```
