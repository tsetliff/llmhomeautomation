from llmhomeautomation.modules.module import Module
import subprocess
import os

# Add the personality to tell the system that it does home automation.
class Espeak(Module):
    def __init__(self):
        self.playback_device = os.getenv("PLAYBACK_DEVICE")
        super().__init__()

    def owns(self) -> list:
        return ["speaking"]

    def process_command_examples(self, command_examples: list) -> list:
        command_examples.append(f"""You may ask to clarify the request or answer in text format using this format:
[{{"response": "Concise answer to the question."}}]""")
        return command_examples

    def process_commands(self, commands: list) -> list:
        # Create a new list excluding commands that contain "response"
        updated_commands = []

        for command in commands:
            if "response" in command:
                self.say(command["response"])  # Process the response
            else:
                updated_commands.append(command)  # Keep commands without "response"

        return updated_commands

    def say(self, text: str):
        subprocess.run(['espeak-ng', '-d', self.playback_device, text])