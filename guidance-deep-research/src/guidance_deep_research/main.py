from pocketflow import Flow, Node

class ChatNode(Node):
    def prep(self, shared):
        if "messages" not in shared:
            shared["messages"] = []
        user_input = input("\n Faahhhh")
        
        shared["messages"].append({"role":"user", "content":user_input})

        print(shared["messages"])

        return shared["messages"]
    def exec(self, messages):
        if messages is None:
            return None

        response = print(messages)
        return response    
    def post (self, shared, prep_res, exec_res):
        if prep_res is None or exec_res is None:
            print("\nSeeYA")
            return None

        print(f"\n Assistant: {exec_res}") 


        shared["messages"].append({"role":"assistant", "content":exec_res})

        return "continue"

chat_node = ChatNode()
chat_node - "continue" >> chat_node

flow = Flow(start = chat_node)

if __name__ == "__main__":
    print("Welcome to the Chat Flow! Type 'exit' to quit.")
    shared = {}
    flow.run(shared)