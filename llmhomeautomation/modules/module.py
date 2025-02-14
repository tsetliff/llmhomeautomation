class Module:
    def __init__(self):
        pass

    def enabled(self) -> bool:
        return True

    # A list of strings indicating what services are owned indicating only one module may do them at a time
    def owns(self) -> list:
        return []

    def process_history(self, history: list) -> list:
        return history

    # Message type request
    def process_whoami(self, whoami: list) -> list:
        return whoami

    # Message type request
    def process_request(self, request: dict) -> dict:
        return request

    # The state of the system
    def process_status(self, status: dict) -> dict:
        return status

    # Examples of commands
    def process_command_examples(self, command_examples: list) -> list:
        return command_examples

    def llm_request(self, messages: list, model: str = "gpt-4o") -> str | None:
        return None

    def process_response(self, response: dict) -> dict:
        return response

    def process_commands(self, commands: list) -> list:
        return commands