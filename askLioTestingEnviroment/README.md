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

## Local Usage

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the server:
    ```bash
    python3 simulation_server.py
    ```
3.  Open `index.html` in your browser.
