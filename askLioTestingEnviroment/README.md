# AskLio Simulation Environment

This directory contains a simulation environment that orchestrates a negotiation between a User, the AskLio API (acting as a Vendor), and the Llama Connector (acting as an AI Assistant).

## Components

- **`simulation_server.py`**: A WebSocket server (Port 8768) that manages the message flow.
- **`index.html`**: A web frontend for visualizing the chat and AI hints.
- **`requirements.txt`**: Python dependencies.

## Architecture

1.  **User** sends a message via `index.html`.
2.  **Server** forwards it to:
    - **AskLio API**: To get the vendor's response.
    - **Llama Connector**: To get real-time analysis/hints for the user.
3.  **Server** sends responses back to `index.html` as they arrive.

## Prerequisites

- **Llama Connector**: Must be running on port 8767 (or configured URI).
- **AskLio API**: Accessible via internet.

## Usage

1.  **Start the Server**:
    ```bash
    python3 simulation_server.py
    ```

2.  **Connect Client**:
    - Connect your existing frontend to `ws://<server-ip>:8768`.
    - Or use the provided `test_simulation_client.py`.

3.  **Visualize Negotiation**:
    - Open `http://<server-ip>:8768/` in your browser.
    - This page shows the live conversation and AI hints in real-time.
