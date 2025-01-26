import json
import asyncio
import websockets
from llmhomeautomation.modules.module import Module

class Broadcast(Module):
    def __init__(self):
        super().__init__()

    def owns(self) -> list:
        return ["speak_broadcast"]

    def process_command_examples(self, command_examples: list) -> list:
            command_examples.append(f"""You may ask to clarify the request or answer in text format using this format:
[{{"say": "Concise answer to the question."}}]""")
            return command_examples

    def process_commands(self, commands: list) -> list:
        for command in commands:
            if "say" in command:
                location = command.get("location")
                role = command.get("role")
                message = command["say"]
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(self.send_message(location, role, message))
                else:
                    loop.run_until_complete(self.send_message(location, role, message))
        return commands

    async def send_message(self, location: str, role: str, message: str):
        async with websockets.connect("ws://localhost:8765") as websocket:
            request = json.dumps({"role": role, "type": "say", "location": location, "message": message})
            await websocket.send(request)
