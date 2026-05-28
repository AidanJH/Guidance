import warnings

from nodes import TaskDecompositionNode
from pocketflow import Flow


def create_task_decomposition_flow():
    # Create a TaskDecompositionNode
    task_decomp_node = TaskDecompositionNode(max_retries=1, wait=10)

    # Suppress the expected UserWarning from PocketFlow when flow terminates via the 'end' action with no registered successor
    warnings.filterwarnings("ignore", category=UserWarning, module="pocketflow")

    # Connect the node to itself for the "continue" action
    task_decomp_node - "continue" >> task_decomp_node

    # Create the flow
    task_decomp_flow = Flow(start=task_decomp_node)
    return task_decomp_flow
