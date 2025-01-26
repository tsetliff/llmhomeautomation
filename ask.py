import asyncio
import json
import os
import socket
import readline
import websockets

async def send_message():
    uri = "ws://localhost:8765"
    try:
        while True:
            message = input("Enter your message: ").strip()
            user = os.getlogin()
            hostname = socket.gethostname()
            pid = os.getpid()
            location = f"{user}@{hostname}@{pid}"
            request = json.dumps({"role": "user", "type": "request", "location": location, "message": message})
            async with websockets.connect(uri) as websocket:
                await websocket.send(request)
                print(f"Sent: {request}")
    except KeyboardInterrupt:
        print("\nStopped sending messages.")

if __name__ == "__main__":
    asyncio.run(send_message())
