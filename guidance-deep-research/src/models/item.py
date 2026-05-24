from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from beanie import Document
from pydantic import BaseModel, Field


class StatusEnum(str, Enum):
    pending = "Pending"
    in_progress = "In Progress"
    done = "Done"
    cancelled = "Cancelled"
    needs_info = "Further Information Needed"


class PriorityEnum(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class UrlReference(BaseModel):
    search_query: str
    url: str


class Goal(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    # Fields TBD — Goal is a placeholder in the current UML

    class Settings:
        name = "goals"


class Task(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    display_text: str
    description: str
    status: StatusEnum
    priority: PriorityEnum
    source_input: str
    created_at: datetime
    updated_at: datetime
    participants: list[str] = Field(default_factory=list)
    due_dates: list[date] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    goal_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    priority_reasoning: Optional[str] = None
    hard_deadline: Optional[date] = None
    life_domain: Optional[str] = None

    class Settings:
        name = "tasks"


class Event(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    priority: PriorityEnum
    status: StatusEnum
    participants: list[str] = Field(default_factory=list)

    class Settings:
        name = "events"


class TimeSlot(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    day: int
    month: int
    year: int
    hour: int
    minute: int
    item_ids: list[str] = Field(default_factory=list)
    assigned: bool = False

    class Settings:
        name = "time_slots"


class Calendar(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    item_ids: list[str] = Field(default_factory=list)
    time_slot_ids: list[str] = Field(default_factory=list)

    class Settings:
        name = "calendars"


class DeepResearchResult(Document):
    id: str = Field(default_factory=lambda: str(uuid4()))
    result: str
    chapters: list[str] = Field(default_factory=list)
    url_references: list[UrlReference] = Field(default_factory=list)

    class Settings:
        name = "deep_research_results"
