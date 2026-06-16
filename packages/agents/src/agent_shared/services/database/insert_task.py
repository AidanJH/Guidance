"""Insert a sample task: poetry run python -m agent_shared.services.database.insert_task"""

import asyncio
from datetime import datetime

from shared_contracts import PriorityEnum, StatusEnum, Task

from agent_shared.services.database import close_db, init_db


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
