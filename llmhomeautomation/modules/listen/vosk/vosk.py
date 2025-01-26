from dotenv import load_dotenv
load_dotenv()

import json
import os
import queue
import sounddevice as sd
import sys
import time
import vosk
import asyncio
import socket
import websockets

from llmhomeautomation.modules.module import Module

vosk_model = "./data/" + os.getenv("VOSK_MODEL")
wake_words = os.getenv("AI_NAME").lower().split(",")
record_device = os.getenv("RECORD_DEVICE")

class Vosk(Module):
    def __init__(self):
        self.listening = True
        self.voice_text = []

    def owns(self) -> list:
        return ["listen"]

    def process_command_examples(self, command_examples: list) -> list:
        command_examples.append(f"""You may ask to clarify the request or answer in text format using this format:
[{{"response": "Concise answer to the question."}}]""")
        return command_examples

    async def send_request(self, message):
        async with websockets.connect("ws://localhost:8765") as websocket:
            user = os.getlogin()
            hostname = socket.gethostname()
            location = f"{user}@{hostname}@audio"
            request = json.dumps({"role": "user", "type": "request", "location": location, "message": message})
            await websocket.send(request)

    def listen(self):
        if not os.path.exists(vosk_model):
            print(f"Error: Model directory '{vosk_model}' not found.")
            sys.exit(1)

        model = vosk.Model(vosk_model)
        audio_queue = queue.Queue()

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}", file=sys.stderr)
            if self.listening:
                audio_queue.put(bytes(indata))

        with sd.RawInputStream(
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=audio_callback,
            device=record_device
        ):
            device_info = sd.query_devices(record_device, 'input')
            sample_rate = int(device_info['default_samplerate'])

            print(f"Listening with sample rate of {sample_rate}... Press Ctrl+C to stop.")
            rec = vosk.KaldiRecognizer(model, sample_rate)
            try:
                while True:
                    data = audio_queue.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        self.add_string(result.get('text', ''))
                        self.remove_old_messages()
                        message = self.check_for_keyword()
                        if message:
                            print(message)
                            asyncio.run(self.send_request(message))
                    else:
                        partial_result = json.loads(rec.PartialResult())
                        print(f"Partial: {partial_result.get('partial', '')}", end="\r")
            except KeyboardInterrupt:
                print("\nStopped listening.")

    def add_string(self, input_string):
        current_time = int(time.time())
        self.voice_text.append((input_string, current_time))

    def remove_old_messages(self):
        current_time = int(time.time())
        self.voice_text = [(s, t) for s, t in self.voice_text if current_time - t <= 5]

    def check_for_keyword(self):
        concatenated_string = " ".join([s for s, _ in self.voice_text])
        for wake_word in wake_words:
            if wake_word in concatenated_string:
                # Clear voice_text after detecting a keyword to prevent repeated sends
                message = concatenated_string.split(wake_word, 1)[1].strip().lower()
                self.voice_text.clear()
                return message
        return None

if __name__ == "__main__":
    Vosk().listen()
