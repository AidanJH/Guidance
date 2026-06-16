import warnings

from pocketflow import AsyncFlow

from flows.task_assign.nodes import PersistTasksNode, TaskAssignNode


def create_assign_flow():
    warnings.filterwarnings("ignore", category=UserWarning, module="pocketflow")

    decomp_node = TaskAssignNode(max_retries=1, wait=10)
    persist_node = PersistTasksNode(max_retries=1, wait=5)

    decomp_node - "persist" >> persist_node

    return AsyncFlow(start=decomp_node)
