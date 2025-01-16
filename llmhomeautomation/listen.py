import json
import os
import queue
import sounddevice as sd
import sys
import time
import vosk

from dotenv import load_dotenv
from .modules.module_manager import ModuleManager

# Must load before my modules that directly access the environment
load_dotenv()

from .get_command import GetCommand

vosk_model = "./data/" + os.getenv("VOSK_MODEL")
wake_words = os.getenv("AI_NAME").lower().split(",")
record_device = os.getenv("RECORD_DEVICE")

print(f"using model {vosk_model} for wake words {wake_words}")

RECORD_TIME_SECONDS = 5

class Listen():
    SAMPLE_RATE = 16000  # Sample rate for microphone input

    def __init__(self):
        self.listening = True
        self.voice_text = []

    def go(self):
        ModuleManager()

        # Ensure the Vosk model directory exists
        if not os.path.exists(vosk_model):
            print(f"Error: Model directory '{vosk_model}' not found.")
            print("Download a Vosk model from https://alphacephei.com/vosk/models")
            print("and extract it into the current directory.")
            sys.exit(1)

        # Load the Vosk model
        print("Loading Vosk model...")
        model = vosk.Model(vosk_model)

        # Initialize the audio queue
        audio_queue = queue.Queue()

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}", file=sys.stderr)
            # Add audio data to the queue
            if self.listening:
                audio_queue.put(bytes(indata))

        # Set up the microphone stream
        print("Opening recording device...")
        with sd.RawInputStream(
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=audio_callback,
            device=record_device
        ):
            device_info = sd.query_devices(record_device, 'input')
            sample_rate = int(device_info['default_samplerate'])

            print(f"Listening with sample ratre of {sample_rate}... Press Ctrl+C to stop.")
            rec = vosk.KaldiRecognizer(model, sample_rate)
            try:
                while True:
                    # Get audio data from the queue
                    data = audio_queue.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        print(f"Recognized: {result.get('text', '')}")
                        self.add_string(result.get('text', ''))
                        self.remove_old_messages()
                        message = self.check_for_keyword()
                        print(message)
                        if message:
                            request = {"role": "user", "type": "request", "location": "", "message": message}
                            commands = GetCommand().getCommandList(request)
                            if commands:
                                self.listening = False
                                ModuleManager().process_commands(commands)
                                self.listening = True
                    else:
                        partial_result = json.loads(rec.PartialResult())
                        print(f"Partial: {partial_result.get('partial', '')}", end="\r")
            except KeyboardInterrupt:
                print("\nStopped listening.")

    def add_string(self, input_string):
        current_time = int(time.time())  # Get current Unix timestamp
        self.voice_text.append((input_string, current_time))

    def remove_old_messages(self):
        current_time = int(time.time())
        self.voice_text = [(s, t) for s, t in self.voice_text if current_time - t <= 5]

    def check_for_keyword(self):
        print(self.voice_text)
        concatenated_string = " ".join([s for s, _ in self.voice_text])  # Concatenate strings
        print("Made string " + concatenated_string)
        for wake_word in wake_words:
            if wake_word in concatenated_string:
                # Find the portion after the keyword
                return wake_word + " " + concatenated_string.split(wake_word, 1)[1].strip().lower()
        return None

if __name__ == "__main__":
    Listen().go()

