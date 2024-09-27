# websocket_server.py
import asyncio
import websockets
import json

async def echo(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Received data: {data}")
            await websocket.send(message)  # Echo the message back
    except websockets.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"Server Error: {e}")

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
