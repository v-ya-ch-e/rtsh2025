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

# HTML Template for Integrated Chat
VISUALIZER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Negotiation Simulation</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f0f2f5; display: flex; height: 100vh; box-sizing: border-box; }
        #chat-container { flex: 2; display: flex; flex-direction: column; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-right: 20px; overflow: hidden; }
        #messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message-row { display: flex; flex-direction: column; }
        .message-row.user { align-items: flex-end; }
        .message-row.vendor { align-items: flex-start; }
        .bubble { max-width: 70%; padding: 12px 18px; border-radius: 18px; position: relative; font-size: 1rem; line-height: 1.4; }
        .user .bubble { background-color: #0084ff; color: white; border-bottom-right-radius: 4px; }
        .vendor .bubble { background-color: #e4e6eb; color: black; border-bottom-left-radius: 4px; }
        .author-label { font-size: 0.75rem; color: #65676b; margin-bottom: 4px; margin-left: 4px; margin-right: 4px; }
        
        #input-area { padding: 20px; border-top: 1px solid #ddd; display: flex; gap: 10px; background: #fff; }
        #message-input { flex: 1; padding: 15px; border: 1px solid #ddd; border-radius: 25px; outline: none; font-size: 1rem; }
        #send-btn { padding: 10px 25px; background-color: #0084ff; color: white; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; font-size: 1rem; }
        #send-btn:hover { background-color: #0073e6; }
        
        #hints-container { flex: 1; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .hint-card { background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 15px; border-left: 5px solid gray; }
        .hint-card.red { border-left-color: #ff4d4d; background-color: #fff0f0; }
        .hint-card.green { border-left-color: #4caf50; background-color: #f0fff0; }
        .hint-card.yellow { border-left-color: #ffc107; background-color: #fffff0; }
        .hint-title { font-weight: bold; margin-bottom: 5px; font-size: 0.9em; color: #555; }
        h3 { margin-top: 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
    </style>
</head>
<body>

<div id="chat-container">
    <div id="messages"></div>
    <div id="input-area">
        <input type="text" id="message-input" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
        <button id="send-btn" onclick="sendMessage()">Send</button>
    </div>
</div>

<div id="hints-container">
    <h3>AI Analysis & Hints</h3>
    <div id="hints-list"></div>
</div>

<script>
    const ws = new WebSocket("ws://" + window.location.host);
    const messagesDiv = document.getElementById("messages");
    const hintsDiv = document.getElementById("hints-list");
    const input = document.getElementById("message-input");

    ws.onopen = () => {
        addSystemMessage("Connected to Simulation Server");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === "system") {
            addSystemMessage(data.content);
        } else if (data.type === "message") {
            addMessage(data.text, data.author);
        } else if (data.type === "hint") {
            addHint(data.data, data.author);
        }
    };

    function sendMessage() {
        const text = input.value.trim();
        if (!text) return;
        
        // Display user message immediately
        addMessage(text, "user");
        
        // Send to server
        ws.send(JSON.stringify({ text: text }));
        input.value = "";
    }

    function handleKeyPress(e) {
        if (e.key === "Enter") sendMessage();
    }

    function addMessage(text, author) {
        const row = document.createElement("div");
        row.className = `message-row ${author}`;
        
        let html = `<div class="author-label">${author === 'user' ? 'You' : 'Vendor'}</div>`;
        html += `<div class="bubble">${text}</div>`;
        
        row.innerHTML = html;
        messagesDiv.appendChild(row);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function addSystemMessage(text) {
        const div = document.createElement("div");
        div.style.textAlign = "center";
        div.style.color = "#888";
        div.style.fontSize = "0.8em";
        div.style.margin = "10px 0";
        div.innerText = text;
        messagesDiv.appendChild(div);
    }

    function addHint(data, author) {
        const div = document.createElement("div");
        const color = data.MESSAGE_COLOR || "gray";
        div.className = `hint-card ${color}`;
        
        const title = author === 'user' ? "Analysis of your message" : "Analysis of Vendor's message";
        
        div.innerHTML = `
            <div class="hint-title">${title}</div>
            <div>${data.MESSAGE}</div>
        `;
        hintsDiv.insertBefore(div, hintsDiv.firstChild);
    }
</script>

</body>
</html>
"""

class SimulationServer:
    def __init__(self):
        self.conversation_id = None
        self.asklio_conversation_id = None
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
                self.vendor_id = vendors[4]["id"]

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
                self.asklio_conversation_id = conversation["id"]
                logger.info(f"Initialized AskLio conversation: {self.asklio_conversation_id}")

            # 3. Create Local Conversation
            async with session.post(
                "http://localhost:8000/conversations",
                json={"vendor_id": self.vendor_id}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.conversation_id = data["id"]
                    logger.info(f"Initialized Local conversation: {self.conversation_id}")
                else:
                    logger.error(f"Failed to create local conversation: {await resp.text()}")
                    self.conversation_id = 999 # Fallback

            return True

    async def send_to_asklio(self, text):
        """Send message to AskLio and get response"""
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                f"{ASKLIO_API_BASE}/messages/{self.asklio_conversation_id}",
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
                    "company_id": 2,
                    "author": author
                }
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                return json.loads(response)
        except Exception as e:
            logger.error(f"Llama connection error: {e}")
            return {"MESSAGE_COLOR": "gray", "MESSAGE": "Llama unavailable"}

    async def index_handler(self, request):
        # Check for WebSocket upgrade
        if request.headers.get("Upgrade", "").lower() == "websocket":
            return await self.websocket_handler(request)
        # Otherwise serve Integrated Chat
        return web.Response(text=VISUALIZER_HTML, content_type='text/html')

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
                    
                    # Send hint back to WS client
                    await ws.send_json({"type": "hint", "author": "user", "data": llama_res_user})

                    # 2. Send to AskLio
                    vendor_text = await self.send_to_asklio(user_text)
                    
                    if vendor_text:
                        # 3. Process Vendor Message
                        llama_res_vendor = await self.get_llama_hint(vendor_text, "vendor")
                        
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
        
        logger.info(f"Simulation server running on port {SIMULATION_PORT}")
        web.run_app(app, port=SIMULATION_PORT)

if __name__ == "__main__":
    server = SimulationServer()
    server.run()
