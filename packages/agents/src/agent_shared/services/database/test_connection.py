"""Quick smoke test — run with: poetry run python -m agent_shared.services.database.test_connection"""

import asyncio
from datetime import datetime

from shared_contracts import PriorityEnum, StatusEnum, Task

from agent_shared.services.database import close_db, init_db


async def main():
    print("Connecting to MongoDB...")
    await init_db()
    print("Connected.")

    task = Task(
        display_text="Test task",
        description="Created by test_connection.py",
        status=StatusEnum.pending,
        priority=PriorityEnum.medium,
        source_input="manual test",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    await task.insert()
    print(f"Inserted task: {task.id}")

    found = await Task.get(task.id)
    assert found is not None, "Task not found after insert"
    print(f"Retrieved task: {found.display_text}")

    await task.delete()
    print("Deleted task. All good!")

    close_db()


asyncio.run(main())
