"""Fetch and print all tasks: poetry run python src/database/get_tasks.py"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import close_db, init_db
from models.item import Task


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
