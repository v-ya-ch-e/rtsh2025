import asyncio
import websockets
import json

async def hello():
    uri = "ws://3.67.9.62:8767"
    async with websockets.connect(uri) as websocket:
        # Read input from file to simulate real usage
        try:
            input_text = open("text_block1", "r").read()
        except FileNotFoundError:
            input_text = "This is a test message for the negotiation assistant."

        # Send JSON object
        message = {
            "conv_id": 1,
            "text": input_text
        }
        
        print(f"Sending message: {json.dumps(message)[:50]}...")
        await websocket.send(json.dumps(message))
        print("Message sent. Waiting for response...")
        
        response = await websocket.recv()
        print(f"Received response:\n{response}")

if __name__ == "__main__":
    asyncio.run(hello())
