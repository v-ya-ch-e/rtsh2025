# Sekundant (formerly rtsh2025)

**Sekundant** is a comprehensive, real-time negotiation assistant designed to help buyers secure the best deals. It leverages advanced AI (Claude 3 Haiku & Sonnet via AWS Bedrock) to analyze conversations, detect manipulative tactics, verify facts, and provide strategic, actionable advice in real-time.

## Architecture

The system is composed of three microservices:

1.  **Llama Connector (`llama-connector/`)**:
    - **Role**: The "Brain". Handles AI logic, prompt engineering, and AWS Bedrock integration.
    - **Tech**: Python, WebSocket (Port 8767), AWS Bedrock, AsyncIO.
    - **Key Features**: Parallel analysis (Suspicion, Suggestion, Fact-Checking), Unified Keyword System, Hint Saving.

2.  **FastAPI Hands (`fast-api-hands/`)**:
    - **Role**: The "Backbone". Manages data, storage, and API endpoints.
    - **Tech**: FastAPI (Port 8000), MySQL.
    - **Key Features**: Company management, Document storage, Keyword management, Conversation tracking, Conversation Summarization.

3.  **Simulation Environment (`askLioTestingEnviroment/`)**:
    - **Role**: The "Playground". A testing suite for validating the AI.
    - **Tech**: Python, WebSocket (Port 8768), HTML/JS Frontend.
    - **Key Features**: Simulated chat interface, Real-time visualization of AI hints.

## Key Features

- **Real-Time Strategic Advice**: The AI analyzes every message and suggests the next best move (e.g., "Counter-anchor at $500").
- **Bluff Detection**: Identifies inconsistencies and manipulative tactics used by the vendor.
- **Unified Keyword System**: Uses company-specific keywords (facts, tactics, history) to ground advice in reality.
- **Author Awareness**: Distinguishes between the Buyer (User) and Seller (Vendor) to provide context-aware guidance.
- **Conditional Silence**: The AI knows when to stay quiet ("NO_RESPONSE") to avoid overwhelming the user.
- **Document Management**: Upload and manage vendor documents (PDFs, etc.) via a dashboard.
- **Conversation Summary**: Generates high-quality summaries of negotiations using Claude 3.5 Sonnet.

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
- **Database**: Create a MySQL database and update `dbcreds.py` in `llama-connector` and `fast-api-hands`.
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
- **Simulation UI**: Open `http://localhost:8768/` to test the negotiation assistant.
- **Document Dashboard**: Open `document_dashboard/index.html` to manage companies and documents.

## Documentation
- [Llama Connector README](llama-connector/README.md)
- [FastAPI Hands README](fast-api-hands/README.md)
- [Simulation README](askLioTestingEnviroment/README.md)