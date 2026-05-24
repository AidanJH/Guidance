"""Insert a sample task: poetry run python src/database/insert_task.py"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import close_db, init_db
from models.item import PriorityEnum, StatusEnum, Task


async def main():
    await init_db()

    task = Task(
        display_text="Eat healthy",
        description=(
            "User wants to improve their diet. They are overweight, mid-30s male, "
            "enjoy sweets, eat mostly takeout 3x/day, and were recently advised by "
            "their doctor to eat healthier."
        ),
        status=StatusEnum.pending,
        priority=PriorityEnum.high,
        source_input="Help me eat healthy",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        life_domain="Health",
    )

    await task.insert()
    print(f"Inserted: {task.id}")
    print(f"  display_text : {task.display_text}")
    print(f"  status       : {task.status}")
    print(f"  priority     : {task.priority}")
    print(f"  life_domain  : {task.life_domain}")

    close_db()


asyncio.run(main())
