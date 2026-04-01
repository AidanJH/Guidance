import json

from pocketflow import Flow, Node
from guidance_deep_research.utils import call_llm
class ChainOfThoughtNode(Node):
    def prep(self, shared):
        if "problem_statement" not in shared:
            shared["problem_statement"] = []
            
        if "thoughts" not in shared:
            shared["thoughts"] = []
            shared["thought_number"] = 0
            user_input = input("You:")
            shared["problem_statement"].append({"role":"assistant", "content":user_input})
            
        # If we are at thought 0, we havent had a thought yet, so we need to do the first thought prompt
            # We need to read the user input to get the problem statement
            # We need to create a prompt and include the problem statement in the prompt
            
        print("You:")

    def exec(self, messages):
        print("Assistant:")
    
    def post (self, shared, prep_res, exec_res):
    
        return "continue"

chat_node = ChainOfThoughtNode()
chat_node - "continue" >> chat_node

flow = Flow(start = chat_node)

if __name__ == "__main__":
    print("Welcome to the Chat Flow! Type 'exit' to quit.")
    shared = {}
    flow.run(shared)
    