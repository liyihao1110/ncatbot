#我测试用的，别管
import asyncio
import websockets

async def listen():
    uri = "ws://localhost:3001"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print("Received:", message)

asyncio.get_event_loop().run_until_complete(listen())


