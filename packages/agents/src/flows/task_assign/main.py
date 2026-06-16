import asyncio
import sys
from pathlib import Path

from agent_shared.services.database import close_db, init_db
from dotenv import load_dotenv
from flows.task_assign.flow import create_assign_flow

load_dotenv(Path(__file__).parent / ".env")

USER_CONTEXT = (
    "Person is relatively unhealthy, overweight, mid-30s male. "
    "User enjoys sweets. Recently told by doctor to eat healthy. "
    "Eats 3 meals a day, largely takeout."
)


async def main():
    default_question = "I want to eat healthy, help me create a meal plan"
    question = default_question
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            question = arg[2:]
            break

    print(f"Processing: {question}")

    flow = create_assign_flow()
    shared = {
        "task_from_user": question,
        "context": USER_CONTEXT,
    }

    await init_db()
    try:
        await flow.run_async(shared)
    finally:
        close_db()

    print("\nDone. Task IDs saved to shared['persisted_task_ids']")


if __name__ == "__main__":
    asyncio.run(main())
