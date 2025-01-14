from llmhomeautomation.modules.module import Module

# Add the personality to tell the system that it does home automation.
class Home(Module):
    def __init__(self):
        super().__init__()

    def process_whoami(self, whoami: list) -> list:
        home_string = f"""You are a home automation machine that returns a list of commands for the house to run based on a users request.
        You may however answer any question even if it is not related to home automation."""
        whoami.append(home_string)
        return whoami

    # The state of the system
    def process_status(self, status: dict) -> dict:
        return status

    def process_command_examples(self, command_examples: list) -> list:
        return command_examples