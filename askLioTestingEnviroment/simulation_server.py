import asyncio
import json
import logging
import aiohttp
from aiohttp import web
import websockets

# Configuration
ASKLIO_API_BASE = "https://negbot-backend-ajdxh9axb0ddb0e9.westeurope-01.azurewebsites.net/api"
ASKLIO_TEAM_ID = 823044
LLAMA_URI = "ws://localhost:8767"
SIMULATION_PORT = 8768

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SimulationServer")

# HTML Template for Visualizer
VISUALIZER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Negotiation Visualizer</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f0f2f5; }
        #container { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        h1 { text-align: center; color: #333; padding: 20px; margin: 0; border-bottom: 1px solid #eee; }
        #messages { padding: 20px; height: 70vh; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message-row { display: flex; flex-direction: column; }
        .message-row.user { align-items: flex-end; }
        .message-row.vendor { align-items: flex-start; }
        .bubble { max-width: 70%; padding: 12px 18px; border-radius: 18px; position: relative; font-size: 1rem; line-height: 1.4; }
        .user .bubble { background-color: #0084ff; color: white; border-bottom-right-radius: 4px; }
        .vendor .bubble { background-color: #e4e6eb; color: black; border-bottom-left-radius: 4px; }
        .author-label { font-size: 0.75rem; color: #65676b; margin-bottom: 4px; margin-left: 4px; margin-right: 4px; }
        .hint-box { margin-top: 5px; padding: 10px; border-radius: 8px; font-size: 0.9rem; max-width: 70%; border-left: 4px solid #ccc; background-color: #f9f9f9; }
        .hint-box.red { border-left-color: #ff4d4d; background-color: #fff0f0; }
        .hint-box.green { border-left-color: #4caf50; background-color: #f0fff0; }
        .hint-box.yellow { border-left-color: #ffc107; background-color: #fffff0; }
        .hint-title { font-weight: bold; margin-bottom: 2px; font-size: 0.8rem; color: #555; }
    </style>
</head>
<body>
    <div id="container">
        <h1>Live Negotiation</h1>
        <div id="messages"></div>
    </div>

    <script>
        const messagesDiv = document.getElementById("messages");
        const evtSource = new EventSource("/events");

        evtSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'history') {
                messagesDiv.innerHTML = '';
                data.messages.forEach(msg => addMessageToUI(msg));
            } else if (data.type === 'new_message') {
                addMessageToUI(data.message);
            }
        };

        function addMessageToUI(msg) {
            const row = document.createElement("div");
            row.className = `message-row ${msg.author === 'user' ? 'user' : 'vendor'}`;
            
            let html = `<div class="author-label">${msg.author === 'user' ? 'User' : 'Vendor'}</div>`;
            html += `<div class="bubble">${msg.text}</div>`;
            
            if (msg.hint) {
                const color = msg.hint.MESSAGE_COLOR || "gray";
                html += `
                    <div class="hint-box ${color}">
                        <div class="hint-title">AI Analysis</div>
                        ${msg.hint.MESSAGE}
                    </div>
                `;
            }
            
            row.innerHTML = html;
            messagesDiv.appendChild(row);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    </script>
</body>
</html>
"""

class SimulationServer:
    def __init__(self):
        self.conversation_id = None
        self.vendor_id = None
        self.history = [] # List of {author, text, hint}
        self.sse_queues = set()

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

    async def broadcast_update(self, message_obj):
        """Send update to all SSE clients"""
        self.history.append(message_obj)
        data = json.dumps({"type": "new_message", "message": message_obj})
        for queue in self.sse_queues:
            await queue.put(data)

    async def index_handler(self, request):
        # Check for WebSocket upgrade
        if request.headers.get("Upgrade", "").lower() == "websocket":
            return await self.websocket_handler(request)
        # Otherwise serve Visualizer
        return web.Response(text=VISUALIZER_HTML, content_type='text/html')

    async def sse_handler(self, request):
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
        )
        await response.prepare(request)
        
        queue = asyncio.Queue()
        self.sse_queues.add(queue)
        
        try:
            # Send history first
            await response.write(f"data: {json.dumps({'type': 'history', 'messages': self.history})}\\n\\n".encode('utf-8'))
            
            while True:
                data = await queue.get()
                await response.write(f"data: {data}\\n\\n".encode('utf-8'))
        except Exception as e:
            logger.info(f"SSE connection closed: {e}")
        finally:
            self.sse_queues.remove(queue)
        
        return response

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        logger.info("Client connected via WebSocket")
        
        if not self.conversation_id:
            success = await self.init_asklio()
            if not success:
                await ws.send_json({"type": "system", "content": "Failed to initialize AskLio vendor."})
                return ws

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    user_text = data.get("text")
                    if not user_text:
                        continue

                    # 1. Process User Message
                    llama_res_user = await self.get_llama_hint(user_text, "user")
                    
                    user_msg_obj = {
                        "author": "user",
                        "text": user_text,
                        "hint": llama_res_user
                    }
                    await self.broadcast_update(user_msg_obj)
                    
                    # Send hint back to WS client (optional, but good for consistency)
                    await ws.send_json({"type": "hint", "author": "user", "data": llama_res_user})

                    # 2. Send to AskLio
                    vendor_text = await self.send_to_asklio(user_text)
                    
                    if vendor_text:
                        # 3. Process Vendor Message
                        llama_res_vendor = await self.get_llama_hint(vendor_text, "opponent")
                        
                        vendor_msg_obj = {
                            "author": "vendor",
                            "text": vendor_text,
                            "hint": llama_res_vendor
                        }
                        await self.broadcast_update(vendor_msg_obj)
                        
                        # Send to WS client
                        await ws.send_json({"type": "message", "author": "vendor", "text": vendor_text})
                        await ws.send_json({"type": "hint", "author": "vendor", "data": llama_res_vendor})
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"ws connection closed with exception {ws.exception()}")

        logger.info("Client disconnected")
        return ws

    def run(self):
        app = web.Application()
        app.router.add_get('/', self.index_handler)
        app.router.add_get('/events', self.sse_handler)
        
        logger.info(f"Simulation server running on port {SIMULATION_PORT}")
        web.run_app(app, port=SIMULATION_PORT)

if __name__ == "__main__":
    server = SimulationServer()
    server.run()
