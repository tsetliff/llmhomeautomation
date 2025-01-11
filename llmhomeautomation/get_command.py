from .api_handler import APIHandler
from .modules.module_manager import ModuleManager

class GetCommand:
    def __init__(self):
        pass

    def go(self, request: dict):
        request = ModuleManager().process_request(request)
        status = {}
        status = ModuleManager().process_status(status)

        whoami = []
        whoami_string = " ".join(ModuleManager().process_whoami(whoami))

        command_examples = []
        command_examples.append(f"""You may ask to clarify the request or answer in text format using this format:
[{{"response": "Concise answer to the question."}}]
""")
        command_examples = " ".join(ModuleManager().process_command_examples(command_examples))

        prompt = f"""
{whoami_string}

Current State:
{status}

And commands in this form:
{command_examples}

If you hear the request "{request}"
What commands would you send in JSON format?
"""
        print("Prompt:" + prompt)
        result = APIHandler().get_response(prompt)
        print("Prompt Result:" + result)
        return result