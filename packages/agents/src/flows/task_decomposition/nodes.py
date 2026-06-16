# cookbook/pocketflow-thinking/nodes.py
from agent_shared.prompts import get_prompt
from agent_shared.utils.llm_client import call_llm
from pocketflow import Node


# Helper function to format structured plan for printing
def format_plan(plan_items, indent_level=0):
    return "\n"


# Helper function to format structured plan for the prompt (simplified view)
def format_plan_for_prompt(plan_items, indent_level=0):
    return "\n"


class TaskDecompositionNode(Node):
    def prep(self, shared):
        task_from_user = shared.get("task_from_user", "")

        return {
            "task_from_user": task_from_user,
            "sub-tasks": [],
            "context": "Person is relatively unhealthy, overweight, mid 30s male. User enjoys sweets.User was recently told by doctor to eat healthy.User eats 3 meals a day, largely takeoutUsers schedule for the week",
        }

    def exec(self, prep_res):
        task_from_user = prep_res["task_from_user"]
        sub_tasks = prep_res["sub-tasks"]
        context = prep_res["context"]

        # --- Construct Prompt ---
        prompt_result = get_prompt(
            "task_decomposition",
            context=context,
            task_from_user=task_from_user,
        )
        # --- End Prompt Construction ---

        # Clear screen and display thought header + full prompt
        print("\033[2J\033[H", end="", flush=True)
        print(f"[prompt: {prompt_result.name} v{prompt_result.version}]")
        print(prompt_result.text)

        response = call_llm(prompt_result.text)
        full_response = ""
        for chunk in response:
            if (
                hasattr(chunk.choices[0].delta, "content")
                and chunk.choices[0].delta.content is not None
            ):
                chunk_content = chunk.choices[0].delta.content
                print(chunk_content, end="", flush=True)
                full_response += chunk_content

        print(f"\n{'─' * 62}")
        # Simple YAML extraction
        yaml_str = full_response.split("```yaml")[1].split("```")[0].strip()

        return yaml_str

    def post(self, shared, prep_res, exec_res):

        print(exec_res)
        return "dont_continue"
