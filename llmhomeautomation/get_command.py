import json
import sys

from .api_handler import APIHandler
from .modules.module_manager import ModuleManager

class GetCommand:
    def __init__(self):
        pass

    def getCommandList(self, request: dict, depth = 0) -> list | None:
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
        response = APIHandler().get_response(messages)
        print("Prompt Result:" + response)
        response = ModuleManager().process_response({"role": "assistant", "content": response})

        try:
            commands = json.loads(response["content"])

            # Check if it's a list
            if not isinstance(commands, list):
                raise ValueError("JSON data is not a list.")

            # Check if every item in the list is a dictionary
            if not all(isinstance(item, dict) for item in commands):
                raise ValueError("JSON list does not contain only dictionaries.")
        except Exception as e:
            if depth > 0:
                raise e
            fix_json_request = {"type": "request", "location": request["location"], "message":
f"""
I received invalid json back.  Can you please fix this json that should be an array of objects:
{response}
"""
            }
            commands = self.getCommandList(fix_json_request)
        return commands