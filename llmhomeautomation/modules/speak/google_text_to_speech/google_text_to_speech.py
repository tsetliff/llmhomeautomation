from llmhomeautomation.modules.module import Module
from google.cloud import texttospeech
import subprocess
import os
import re

# Add the personality to tell the system that it does home automation.
class GoogleTextToSpeech(Module):
    def __init__(self, cache_dir: str = "data/google_text_to_speech_cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)  # Ensure the cache directory exists

        self.playback_device = os.getenv("PLAYBACK_DEVICE")
        self.client = texttospeech.TextToSpeechClient()
        super().__init__()

    def owns(self) -> list:
        return ["speak"]

    def process_command_examples(self, command_examples: list) -> list:
        command_examples.append(f"""You may ask to clarify the request or answer in text format using this format:
[{{"say": "Concise answer to the question."}}]""")
        return command_examples

    def process_commands(self, commands: list) -> list:
        for command in commands:
            if "say" in command:
                print(command)
                self.say(command["say"])

        return commands

    def say(self, text: str):
        import hashlib
        import time

        # Clean up old cached files
        current_time = time.time()
        one_month_ago = current_time - (30 * 24 * 60 * 60)  # 30 days ago
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path):
                file_mod_time = os.path.getmtime(file_path)
                if file_mod_time < one_month_ago:
                    os.remove(file_path)
                    print(f"Deleted old cache file: {file_path}")

        # Split text by periods, commas, and new lines
        segments = [segment.strip() for segment in re.split(r'[.,\n]', text) if segment.strip()]

        for segment in segments:
            # Generate a hash for the segment
            segment_hash = hashlib.md5(segment.encode()).hexdigest()
            output_file = os.path.join(self.cache_dir, f"{segment_hash}.wav")

            # Check if the file already exists
            if not os.path.exists(output_file):
                print(f"Recording: {segment}")
                input_text = texttospeech.SynthesisInput(text=segment)

                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name="en-US-Standard-D",
                    ssml_gender=texttospeech.SsmlVoiceGender.MALE
                )

                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16
                )

                response = self.client.synthesize_speech(
                    input=input_text,
                    voice=voice,
                    audio_config=audio_config
                )

                with open(output_file, "wb") as out:
                    out.write(response.audio_content)
                    print(f"Audio content written to {output_file}")
            else:
                print(f"Using Cached Segment: {segment}")
                # Update the modification time of the cached file
                os.utime(output_file, None)

            # Play the audio file
            subprocess.run(['aplay', '-D', self.playback_device, output_file])
