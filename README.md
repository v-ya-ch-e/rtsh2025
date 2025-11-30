# Real-Time Negotiation Assistant (rtsh2025)

This project is a comprehensive real-time negotiation assistant system designed to help buyers get the best deal. It uses advanced AI (Claude 3 Haiku via AWS Bedrock) to analyze conversations, detect bluffs, and provide strategic advice based on company-specific context and knowledge.

## Architecture

The system consists of three main components:

1.  **Llama Connector (`llama-connector/`)**:
    - The core AI logic server.
    - Connects to AWS Bedrock for parallel analysis (Suspicion, Suggestion, Fact-Checking).
    - Exposes a WebSocket API (`ws://localhost:8767`) for real-time communication.
    - Fetches context and knowledge from the Local Storage API.

2.  **FastAPI Hands (`fast-api-hands/`)**:
    - The backend API and storage service.
    - Manages company data, conversations, and documents.
    - Provides **Local Storage** for Context and Knowledge files (`storage/companies/{id}/`).
    - Exposes REST endpoints (`http://localhost:8000`) for the dashboard and other services.

3.  **AskLio Simulation Environment (`askLioTestingEnviroment/`)**:
    - A testing and simulation suite.
    - Includes a **Simulation Server** (`ws://localhost:8768`) that orchestrates the chat between the User, the Vendor (AskLio API), and the AI Assistant.
    - Provides a web frontend (`index.html`) to visualize the negotiation.

## Features

- **Real-Time Analysis**: Instant feedback on vendor messages.
- **Author Awareness**: Distinguishes between Buyer and Seller to give relevant advice.
- **Dynamic Knowledge**: Uses company-specific tactics and facts.
- **Document Management**: Upload and manage company documents via a dashboard.
- **Local Context Storage**: Edit context and knowledge base files directly in the browser.
- **Simulation**: Test the AI against a simulated vendor.

## Quick Start

### 1. Prerequisites
- Python 3.8+
- MySQL Database
- AWS Account (Bedrock Access)

### 2. Installation
Clone the repository and install dependencies for all services:
```bash
pip install -r llama-connector/requirements.txt
pip install -r fast-api-hands/requirements.txt
pip install -r askLioTestingEnviroment/requirements.txt
```

### 3. Configuration
- **Database**: Create a MySQL database and update `dbcreds.py` (copy from template).
- **AWS**: Configure AWS credentials (`aws configure` or env vars).

### 4. Running the System
Start all three services in separate terminals:

**Terminal 1: FastAPI (Data & Storage)**
```bash
cd fast-api-hands
python3 main.py
```

**Terminal 2: Llama Connector (AI Logic)**
```bash
cd llama-connector
python3 main.py
```

**Terminal 3: Simulation Server (UI)**
```bash
cd askLioTestingEnviroment
python3 simulation_server.py
```

### 5. Accessing the Interfaces
- **Document Dashboard**: Open `document_dashboard/index.html` in your browser to manage companies and documents.
- **Simulation UI**: Open `http://localhost:8768/` to test the negotiation assistant.

## Documentation
- [Llama Connector README](llama-connector/README.md)
- [FastAPI Hands README](fast-api-hands/README.md)
- [Simulation README](askLioTestingEnviroment/README.md)
- [Deployment Guide](llama-connector/DEPLOYMENT.md)