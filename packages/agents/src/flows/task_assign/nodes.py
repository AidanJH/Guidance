from datetime import datetime
import json
from uuid import uuid4

import yaml
from agent_shared.utils.llm_client import call_llm
from pocketflow import AsyncNode
from shared_contracts import PriorityEnum, StatusEnum, Task, TaskDecompositionResult

""" 
The Node/Flow should be asking for each property of the of a 
Task ={
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

}  to be able to save it to the database

Input:
"I want to take my dog for a walk"

1. Create a base Task object with the information that we currently have.
createTask()
- Name a description:



Task={
    display_text: "Take dog for a walk"
    description: "I want to take my dog for a walk" | "The user is going to take their dog for a walk"
    status: StatusEnum.TODO
    priority: PriorityEnum.UNKNOWN
    priority_reasoning: "We don't know how important this is to the user yet"
    source_input: "I want to take my dog for a walk"
    created_at: datetime.now()
    updated_at: datetime.now()
    participants: [get_user_from_base_prompt(), (UNKNOWN)] #This would be a tool call, we are looking for the users dog
    due_dates: [UNKNOWN]
    goal_id: UNKNOWN | MAYBE
    parent_task_id: UNKNOWN # Maybe perform a post anaylsis search to see if this might be related to anything, otherwise ask the user if the judgement is that this could be to related to something
    life_domain: Fitness | Pet | Personal Wellbeing # We might wanna park this for now.
}


- When do you have free time?
*ANSWER
-How long do yoiu want  to walk the dog for?

Out - We have a goal, its get as complete as possible Task object
if values are missing fill the blanks.


"""


class TaskAssignNode(AsyncNode):
    async def prep_async(self, shared):
        # Get the task from the user
        task_from_user = shared.get("task_from_user", "")

        shared["created_task"] = Task(
            status=StatusEnum.pending,
            priority=PriorityEnum.high,
            source_input=task_from_user,
            participants=["Tom From MySpace"],
        )
        return {
            "task_from_user": task_from_user,
            "created_task": shared["created_task"],
            "context": shared.get("context", ""),
        }

    async def exec_async(self, prep_response):
        # Call the LLM to create a task object based on the examples provided
        created_task = prep_response["created_task"]
        context = prep_response["context"]

        prompt = f"""
        The block below is a Task yaml object that needs to be filled out.
        Have a look at the source_input field, and use that initial question along with the context to attempt to fill out any of the fields that say 'None'. 
        If you do not have the available knowledge or context to make a decision on a field, just fill it out as 'null'.
        You should return the entire Task object, including the existing filled out fields as a json object.
        Do not print out any reasoning, only print out the Task object itself. 
        Task: {created_task}
        Context: {context}
        """

        # Construct message
        response = call_llm(prompt)

        print("\n===== RAW LLM OUTPUT =====")
        print(response)

        print("===== END RAW LLM OUTPUT =====\n")

        return response

    async def post_async(self, shared, prep_response, exec_response):
        try:
            data = Task.model_validate(exec_response)
            print(data)
            print("DISPLAY: " + data.display_text)
            return "persist"
        except Exception as e:
            print(f"Failed to parse LLM output: {e}")
            return "retry"

class PersistTasksNode(AsyncNode):
    async def prep_async(self, shared):
        return {
            "result": shared.get("decomposition_result"),
            "source_input": shared.get("task_from_user", ""),
        }

    async def exec_async(self, prep_response):
        result: TaskDecompositionResult = prep_response["result"]
        source_input = prep_response["source_input"]

        if result is None:
            return []

        now = datetime.now()

        tasks = []
        return tasks

    async def post_async(self, shared, _prep_response, exec_response):
        return "end"
