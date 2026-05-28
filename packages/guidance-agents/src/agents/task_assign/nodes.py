import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import yaml
from pocketflow import AsyncNode

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import close_db, init_db
from models.item import PriorityEnum, Task
from models.task_decomposition import TaskDecompositionResult
from prompts import get_prompt
from utils import call_llm


class TaskAssignNode(AsyncNode):
    async def prep_async(self, shared):
        return {
            "task_from_user": shared.get("task_from_user", ""),
            "context": shared.get("context", ""),
        }

    async def exec_async(self, prep_res):
        prompt_result = get_prompt(
            "task_assign",
            context=prep_res["context"],
            task_from_user=prep_res["task_from_user"],
        )

        print("\033[2J\033[H", end="", flush=True)
        print(f"[prompt: {prompt_result.name} v{prompt_result.version}]")
        print(prompt_result.text)

        response = call_llm(prompt_result.text)
        full_response = ""
        for chunk in response:
            if (
                hasattr(chunk.choices[0].delta, "content")
                and chunk.choices[0].delta.content is not None
            ):
                chunk_content = chunk.choices[0].delta.content
                print(chunk_content, end="", flush=True)
                full_response += chunk_content

        print(f"\n{'─' * 62}")
        yaml_str = full_response.split("```yaml")[1].split("```")[0].strip()
        return yaml_str

    async def post_async(self, shared, prep_res, exec_res):
        try:
            data = yaml.safe_load(exec_res)
            result = TaskDecompositionResult.model_validate(data)
            shared["decomposition_result"] = result
            shared["task_from_user"] = prep_res["task_from_user"]
            return "persist"
        except Exception as e:
            print(f"Failed to parse LLM output: {e}")
            return "end"


class PersistTasksNode(AsyncNode):
    async def prep_async(self, shared):
        return {
            "result": shared.get("decomposition_result"),
            "source_input": shared.get("task_from_user", ""),
        }

    async def exec_async(self, prep_res):
        result: TaskDecompositionResult = prep_res["result"]
        source_input = prep_res["source_input"]

        if result is None:
            return []

        now = datetime.now()
        id_map = {st.id: str(uuid4()) for st in result.subtasks}

        tasks = []
        for subtask in result.subtasks:
            task = Task(
                id=id_map[subtask.id],
                display_text=subtask.description[:80],
                description=subtask.description,
                status=subtask.status,
                priority=subtask.priority or PriorityEnum.medium,
                source_input=source_input,
                created_at=now,
                updated_at=now,
                dependencies=[id_map[d] for d in subtask.dependencies if d in id_map],
            )
            tasks.append(task)

        await init_db()
        for task in tasks:
            await task.insert()
        close_db()

        return tasks

    async def post_async(self, shared, _prep_res, exec_res):
        tasks = exec_res
        print(f"\nPersisted {len(tasks)} task(s) to MongoDB:")
        for task in tasks:
            print(f"  [{task.id[:8]}...] {task.display_text}")
        shared["persisted_task_ids"] = [t.id for t in tasks]
        return "end"
