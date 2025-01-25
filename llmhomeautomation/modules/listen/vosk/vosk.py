import json
import os
import queue
import sounddevice as sd
import sys
import time
import vosk

from dotenv import load_dotenv
# Must load before modules that directly access the environment
load_dotenv()

from llmhomeautomation.modules.module import Module

from ...get_command import GetCommand

# Add the personality to tell the system that it does home automation.
class Vosk(Module):
    def __init__(self):
        self.playback_device = os.getenv("PLAYBACK_DEVICE")
        self.client = texttospeech.TextToSpeechClient()
        super().__init__()

    def owns(self) -> list:
        return ["listening"]

    def process_command_examples(self, command_examples: list) -> list:
        command_examples.append(f"""You may ask to clarify the request or answer in text format using this format:
[{{"response": "Concise answer to the question."}}]""")
        return command_examples

    def process_commands(self, commands: list) -> list:
        for command in commands:
            if "response" in command:
                print(command)
                self.say(command["response"])  # Process the response

        return commands

    def say(self, text: str):
        # Prevent sending a book to google synthesis
        text = text[:200]

        print("Saying:" + text)
        input_text = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",  # Language and accent
            # https://cloud.google.com/text-to-speech/docs/voices
            # name="en-US-Wavenet-D",  # Wavenet for high-quality voices
            name="en-US-Standard-D",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE  # Gender: MALE, FEMALE, or NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16  # Audio format: MP3, LINEAR16, OGG_OPUS
        )

        response = self.client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config
        )

        output_file = "/tmp/output.wav"

        with open(output_file, "wb") as out:
            out.write(response.audio_content)
            print(f"Audio content written to {output_file}")

        subprocess.run(['aplay', '-D', self.playback_device, '/tmp/output.wav'])