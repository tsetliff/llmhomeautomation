import json
import sys

from .api_handler import APIHandler
from .modules.module_manager import ModuleManager

class GetCommand:
    def __init__(self):
        pass

    def go(self, request: dict) -> str | None:
        request = ModuleManager().process_request(request)
        if request is None:
            return None

        status = {}
        status = ModuleManager().process_status(status)

        whoami = []
        whoami_string = " ".join(ModuleManager().process_whoami(whoami))

        command_examples = []
        command_examples = " ".join(ModuleManager().process_command_examples(command_examples))

        prompt = f"""
{whoami_string}

Current State:
{status}

And commands in this form:
{command_examples}

Please reply in JSON format using an array of commands.
"""
        print("Prompt:" + prompt)
        messages = [
            {
                "role": "system",
                "content": prompt
            },
        ]

        messages = ModuleManager().process_history(messages)

        messages.append(
            {
                "role": "user",
                "content": json.dumps(request)
            }
        )
        result = APIHandler().get_response(messages)
        print("Prompt Result:" + result)
        return result