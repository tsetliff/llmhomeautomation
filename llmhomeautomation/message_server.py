import asyncio
import websockets

connected_clients = set()

async def handle_connection(websocket):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # Create tasks for sending messages to other clients
            tasks = [asyncio.create_task(client.send(message)) for client in connected_clients if client != websocket]
            if tasks:  # Only wait if there are tasks to execute
                await asyncio.wait(tasks)
    except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        connected_clients.remove(websocket)
        print("Client disconnected")

async def main():
    async with websockets.serve(handle_connection, "0.0.0.0", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
