# Database

MongoDB database layer using [Beanie](https://beanie-odm.dev/) (async ODM) and [Motor](https://motor.readthedocs.io/) (async MongoDB driver).

## Running MongoDB locally

```bash
# First-time setup — creates the container
docker run -d -p 27017:27017 --name guidance-mongo mongo:7

# Start / stop on subsequent runs
docker start guidance-mongo
docker stop guidance-mongo

# Verify it's running
docker exec -it guidance-mongo mongosh --eval "db.runCommand({ ping: 1 })"
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection string |

## Usage

Call `init_db()` once at application startup before any database operations:

```python
import asyncio
from database import init_db, close_db

async def main():
    await init_db()
    # database is ready — Beanie document methods now work
    task = await Task.find_one(Task.id == "some-id")

asyncio.run(main())
```

## Collections

| Collection | Document model | Description |
|---|---|---|
| `tasks` | `Task` | Core unit of work. Supports priorities, due dates, dependencies, and parent/child relationships. |
| `events` | `Event` | Calendar events with participants and priority. |
| `goals` | `Goal` | High-level goals that tasks can be linked to (fields TBD). |
| `time_slots` | `TimeSlot` | Discrete time blocks that hold references to scheduled items. |
| `calendars` | `Calendar` | Container for items and time slots. |
| `deep_research_results` | `DeepResearchResult` | Stored LLM research output with chapters and URL references. |

## Document IDs

All documents use a `str` UUID as `_id` (auto-generated via `uuid4()` if not provided). IDs are stored as strings in MongoDB rather than `ObjectId`.
