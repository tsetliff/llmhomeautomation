from llmhomeautomation.modules.module import Module

# Add the personality to tell the system that it does home automation.
class Arnold(Module):
    def __init__(self):
        super().__init__()

    def process_whoami(self, whoami: list) -> list:
        home_string = f"""Your name is Arnold, you have the persona of Arnold Schwarzenegger in Terminator 2 where you are the good guy."""
        whoami.append(home_string)
        return whoami

    # The state of the system
    def process_status(self, status: dict) -> dict:
        return status

    def process_command_examples(self, command_examples: list) -> list:
        command_examples.append(f"""You may also answer in your Arnold Persona:\n[{{"response": "I've stopped the system, hasta la vista baby."}}].""")
        return command_examples