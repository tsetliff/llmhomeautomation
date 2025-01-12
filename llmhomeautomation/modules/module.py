class Module:
    def __init__(self):
        pass

    def enabled(self) -> bool:
        return True

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

    def process_commands(self, commands: list) -> list:
        return commands