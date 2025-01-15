import json

from llmhomeautomation.modules.module import Module

class Context(Module):
    def __init__(self):
        self.history = []
        super().__init__()

    def process_whoami(self, whoami: list) -> list:
        home_string = f"""The user is unable to see the previous entries, the last one provided is there most recent request. I'm sending our previous interactions, they are your history."""
        whoami.append(home_string)
        return whoami

    def process_request(self, request: dict) -> dict:
        self.add_entry(request)
        return request

    def process_response(self, response: dict) -> dict:
        self.add_entry(response)
        return response

    def process_history(self, history: list) -> list:
        for entry in self.history[:-1]:
            print("Entry:")
            print(entry)
            print("End Entry")

            if entry["role"] == "user" and "message" in entry:
                history.append({"role": entry['role'], "content": entry["message"]})
            elif entry["role"] == "assistant":
                content = entry["content"]
                if not isinstance(content, str):
                    content = json.dumps(content)
                history.append({"role": entry['role'], "content": content})
        return history

    def add_entry(self, entry: dict):
        self.history.append(entry)
        self.history = self.history[-6:]