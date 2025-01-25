import os
from llmhomeautomation.modules.module import Module

class Reboot(Module):
    def __init__(self):
        self.inject = False
        super().__init__()

    # Message type request
    def process_request(self, request: dict) -> dict:
        keywords = ["reboot", "restart", "system", "yourself"]
        if any(keyword.lower() in request["message"].lower() for keyword in keywords):
            self.inject = True
        else:
            self.inject_time = False

        return request

    def process_command_examples(self, command_examples: list) -> list:
        command_examples.append(f"""You may reboot your own system with:
[{{"system": "reboot."}}]""")
        return command_examples

    def process_commands(self, commands: list) -> list:
        for command in commands:
            if "system" in command:
                if os.system("sudo -n true") == 0:  # Check for sudo access
                    os.system("sudo reboot")
                else:
                    print("Sudo access is required to reboot the system.")

        return commands

