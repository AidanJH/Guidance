import json

from pocketflow import Flow, Node
from wiki.pocketflow_tutorials.guidance_deep_research.utils import call_llm
class ChatNode(Node):
    def prep(self, shared):
        if "messages" not in shared:
            shared["messages"] = []
        user_input = input("You:")
        
        shared["messages"].append({"role":"user", "content":user_input})

        return shared["messages"]
    def exec(self, messages):
        if messages is None:
            return None

        response = call_llm(messages)
        return response    
    def post (self, shared, prep_res, exec_res):
        if prep_res is None or exec_res is None:
            print("SeeYA")
            return None

        # print(f"\n Assistant: {exec_res}") 

        shared["messages"].append({"role":"assistant", "content":exec_res})

        formatted_json_string = json.dumps(shared["messages"], indent=4)
        print(formatted_json_string)
        return "continue"

chat_node = ChatNode()
chat_node - "continue" >> chat_node

flow = Flow(start = chat_node)

if __name__ == "__main__":
    print("Welcome to the Chat Flow! Type 'exit' to quit.")
    shared = {}
    flow.run(shared)
    