import asyncio
import websockets

async def send_and_receive():
    async with websockets.connect("ws://localhost:8765") as websocket:
        await websocket.send("Hello from client!")
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(send_and_receive())

