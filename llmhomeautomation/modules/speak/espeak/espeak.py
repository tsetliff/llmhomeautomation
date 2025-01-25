from llmhomeautomation.modules.module import Module
import subprocess
import os

class Espeak(Module):
    def __init__(self):
        self.playback_device = os.getenv("PLAYBACK_DEVICE")
        super().__init__()

    def owns(self) -> list:
        return ["speak"]

    def process_command_examples(self, command_examples: list) -> list:
        command_examples.append(f"""You may ask to clarify the request or answer in text format using this format:
[{{"response": "Concise answer to the question."}}]""")
        return command_examples

    def process_commands(self, commands: list) -> list:
        for command in commands:
            if "response" in command:
                self.say(command["response"])  # Process the response

        return commands

    def say(self, text: str):
        subprocess.run(['espeak-ng', '-w', '/tmp/output.wav', text])
        subprocess.run(['aplay', '-D', self.playback_device, '/tmp/output.wav'])