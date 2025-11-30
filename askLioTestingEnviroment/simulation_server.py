import asyncio
import websockets
import json
import aiohttp
import logging

# Configuration
ASKLIO_API_BASE = "https://negbot-backend-ajdxh9axb0ddb0e9.westeurope-01.azurewebsites.net/api"
ASKLIO_TEAM_ID = 823044
LLAMA_URI = "ws://localhost:8767"
SIMULATION_PORT = 8768

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SimulationServer")

class SimulationServer:
    def __init__(self):
        self.conversation_id = None
        self.vendor_id = None

    async def init_asklio(self):
        """Initialize conversation with AskLio"""
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # 1. List vendors
            async with session.get(f"{ASKLIO_API_BASE}/vendors/", params={"team_id": ASKLIO_TEAM_ID}) as resp:
                if resp.status != 200:
                    logger.error(f"Failed to fetch vendors: {await resp.text()}")
                    return False
                vendors = await resp.json()
                if not vendors:
                    logger.error("No vendors found")
                    return False
                self.vendor_id = vendors[0]["id"]

            # 2. Create conversation
            async with session.post(
                f"{ASKLIO_API_BASE}/conversations/",
                params={"team_id": ASKLIO_TEAM_ID},
                json={"vendor_id": self.vendor_id, "title": "Simulation Chat"}
            ) as resp:
                if resp.status not in (200, 201):
                    logger.error(f"Failed to create conversation: {await resp.text()}")
                    return False
                conversation = await resp.json()
                self.conversation_id = conversation["id"]
                logger.info(f"Initialized AskLio conversation: {self.conversation_id}")
                return True

    async def send_to_asklio(self, text):
        """Send message to AskLio and get response"""
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                f"{ASKLIO_API_BASE}/messages/{self.conversation_id}",
                data={"content": text}
            ) as resp:
                if resp.status not in (200, 201):
                    logger.error(f"Failed to send to AskLio: {await resp.text()}")
                    return None
                data = await resp.json()
                return data.get("content")

    async def get_llama_hint(self, text, author):
        """Get hint from Llama Connector"""
        try:
            async with websockets.connect(LLAMA_URI) as websocket:
                message = {
                    "conv_id": self.conversation_id if self.conversation_id else 999,
                    "text": text,
                    "company_id": 1,
                    "author": author
                }
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                return json.loads(response)
        except Exception as e:
            logger.error(f"Llama connection error: {e}")
            return {"MESSAGE_COLOR": "gray", "MESSAGE": "Llama unavailable"}

    async def handler(self, websocket):
        logger.info("Client connected")
        
        # Initialize AskLio on first connection if not ready
        if not self.conversation_id:
            success = await self.init_asklio()
            if not success:
                await websocket.send(json.dumps({
                    "type": "system",
                    "content": "Failed to initialize AskLio vendor."
                }))
                return

        try:
            async for message in websocket:
                data = json.loads(message)
                user_text = data.get("text")
                
                if not user_text:
                    continue

                # 1. Forward User message to Frontend (echo)
                # (Client handles its own display, but we can confirm receipt)
                
                # 2. Get Llama analysis for User message
                llama_task_user = asyncio.create_task(self.get_llama_hint(user_text, "user"))
                
                # 3. Send to AskLio
                asklio_task = asyncio.create_task(self.send_to_asklio(user_text))
                
                # Wait for Llama analysis
                llama_res_user = await llama_task_user
                await websocket.send(json.dumps({
                    "type": "hint",
                    "author": "user",
                    "data": llama_res_user
                }))

                # Wait for AskLio response
                vendor_text = await asklio_task
                if vendor_text:
                    # Send Vendor message to Frontend
                    await websocket.send(json.dumps({
                        "type": "message",
                        "author": "vendor",
                        "text": vendor_text
                    }))
                    
                    # 4. Get Llama analysis for Vendor message
                    llama_res_vendor = await self.get_llama_hint(vendor_text, "opponent")
                    await websocket.send(json.dumps({
                        "type": "hint",
                        "author": "vendor",
                        "data": llama_res_vendor
                    }))

        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")

    async def start(self):
        async with websockets.serve(self.handler, "0.0.0.0", SIMULATION_PORT):
            logger.info(f"Simulation server running on port {SIMULATION_PORT}")
            await asyncio.Future()  # run forever

if __name__ == "__main__":
    server = SimulationServer()
    asyncio.run(server.start())
