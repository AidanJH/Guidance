import warnings

from nodes import PersistTasksNode, TaskAssignNode
from pocketflow import AsyncFlow


def create_assign_flow():
    warnings.filterwarnings("ignore", category=UserWarning, module="pocketflow")

    decomp_node = TaskAssignNode(max_retries=1, wait=10)
    persist_node = PersistTasksNode(max_retries=1, wait=5)

    decomp_node - "persist" >> persist_node

    return AsyncFlow(start=decomp_node)
