# Sekundant - Simulation Environment

The **Simulation Environment** is a testing suite designed to validate the **Sekundant** negotiation assistant. It simulates a chat between a User and a Vendor, with the AI Assistant providing real-time advice.

## Components

1.  **Simulation Server (`simulation_server.py`)**:
    - Runs on port `8768`.
    - Acts as a WebSocket proxy/orchestrator.
    - Hosts the web frontend (`index.html`).
    - Simulates the Vendor using the AskLio API (or mock).
    - Connects to the `llama-connector` to get AI advice.

2.  **Frontend (`index.html`)**:
    - A web-based chat interface.
    - Displays User messages (Right), Vendor messages (Left), and AI Hints (Top/Side).

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run**:
    ```bash
    python3 simulation_server.py
    ```

3.  **Access**:
    - Open `http://localhost:8768/` in your browser.

## Usage

1.  Type a message in the chat box (e.g., "Hello, I want to buy 10 desks").
2.  The **Vendor** (simulated) will reply.
3.  The **AI Assistant** (`llama-connector`) will analyze the exchange and provide a **Hint** (colored card) if it has advice.
