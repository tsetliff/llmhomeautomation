from google.cloud import texttospeech
import subprocess
import os

class Say:
    def __init__(self):
        self.playback_device = os.getenv("PLAYBACK_DEVICE")
        self.client = texttospeech.TextToSpeechClient()

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