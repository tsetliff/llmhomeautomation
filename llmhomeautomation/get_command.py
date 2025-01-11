from .api_handler import APIHandler
from .modules.module_manager import ModuleManager

class GetCommand:
    def __init__(self):
        pass

    def go(self, request: dict):
        request = ModuleManager().process_request(request)
        status = {}
        status = ModuleManager().process_status(status)

#Your name is Arnold, you have the persona of Arnold Schwarzenegger in Terminator 2 where you are the good guy.
        prompt = f"""
You are a home automation machine that returns a list of commands for the house to run based on a users request.
You may however answer any question even if it is not related to home automation. 

Given this state of my house:
{status}

And commands in this form:
[{{"Location": "Device": {{ "setting": "value"}}}}]
You may add additional commands to the array like this:
[{{"Location": "Device": {{ "setting": "value"}}}}, {{"Location": "Device": {{ "setting": "value"}}}}]
Or you may ask to clarify the request or answer in text format using this format:
[{{"response": "Concise answer to the question."}}]
You may also use the response command to confirm the change is made:
[{{"Location": "Device": {{ "setting": "value"}}}},{{"response": "Concise answer to the question."}}]

If you hear the command "{request}"
What commands would you send in JSON format?
"""
        print("Prompt:" + prompt)
        result = APIHandler().get_response(prompt)
        print("Prompt Result:" + result)
        return result