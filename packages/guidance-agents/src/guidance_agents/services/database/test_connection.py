"""Quick smoke test — run with: poetry run python src/database/test_connection.py"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import close_db, init_db
from models.item import PriorityEnum, StatusEnum, Task
from datetime import datetime


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
