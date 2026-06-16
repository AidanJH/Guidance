"""Fetch and print all tasks: poetry run python -m agent_shared.services.database.get_tasks"""

import asyncio

from shared_contracts import Task

from agent_shared.services.database import close_db, init_db


async def main():
    await init_db()

    tasks = await Task.find_all().to_list()

    if not tasks:
        print("No tasks found.")
    else:
        print(f"Found {len(tasks)} task(s):\n")
        for task in tasks:
            print(f"  ID          : {task.id}")
            print(f"  Display     : {task.display_text}")
            print(f"  Status      : {task.status}")
            print(f"  Priority    : {task.priority}")
            print(f"  Life Domain : {task.life_domain}")
            print(f"  Created     : {task.created_at}")
            print()

    close_db()


asyncio.run(main())
