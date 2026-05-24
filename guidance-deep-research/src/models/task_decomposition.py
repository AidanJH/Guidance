from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .item import PriorityEnum, StatusEnum


class SubTask(BaseModel):
    id: int
    description: str
    status: StatusEnum
    priority: PriorityEnum
    dependencies: list[int] = Field(default_factory=list)
    result: Optional[str] = None
    mark: Optional[str] = None
    sub_steps: Optional[list[str]] = None


class TaskDecompositionResult(BaseModel):
    overall_task_assessment: str = Field(alias="Overall Task Assessment")
    subtasks: list[SubTask] = Field(alias="Subtasks")

    model_config = {"populate_by_name": True}
