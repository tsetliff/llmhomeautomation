import asyncio
import json
import websockets

from dotenv import load_dotenv
load_dotenv()

from llmhomeautomation.modules.llm.openai.openai import OpenAILLM
from llmhomeautomation.modules.module_manager import ModuleManager

class GetCommand:
    def __init__(self):
        pass

    def get_command_list(self, request: dict, depth=0) -> list | None:
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
        response = OpenAILLM().llm_request(messages)
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
            fix_json_request = {
                "type": "request",
                "location": request.get("location", ""),
                "message": f"I received invalid json back. Can you please fix this json that should be an array of objects: {response}"
            }
            commands = self.get_command_list(fix_json_request)
        return commands

class Processor:
    def __init__(self, uri="ws://localhost:8765"):
        self.uri = uri

    async def process_messages(self):
        async with websockets.connect(self.uri, ping_interval=20, ping_timeout=20) as websocket:
            try:
                while True:
                    message = await websocket.recv()
                    print(f"Received: {message}")
                    request = json.loads(message)
                    commands = GetCommand().get_command_list(request)
                    if commands:
                        ModuleManager().process_commands(commands)
            except KeyboardInterrupt:
                print("WebSocket listener stopped.")

if __name__ == "__main__":
    processor = Processor()
    asyncio.run(processor.process_messages())
