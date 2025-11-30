import asyncio
import websockets
import json

async def test_simulation():
    uri = "ws://localhost:8768"
    async with websockets.connect(uri) as websocket:
        print("Connected to Simulation Server")
        
        # Send a message
        msg = {"text": "Hello, I am interested in your product."}
        await websocket.send(json.dumps(msg))
        print(f"Sent: {msg}")
        
        # Listen for responses
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=20.0)
                data = json.loads(response)
                print(f"Received: {data}")
                
                if data.get("type") == "message" and data.get("author") == "vendor":
                    print("Got vendor response, test successful.")
                    break
            except asyncio.TimeoutError:
                print("Timeout waiting for response")
                break

if __name__ == "__main__":
    asyncio.run(test_simulation())
