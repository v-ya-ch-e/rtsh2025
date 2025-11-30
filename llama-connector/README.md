# Llama Connector

The **Llama Connector** is the core AI logic server for the `rtsh2025` negotiation assistant. It connects to **AWS Bedrock** (Claude 3 Haiku) to analyze negotiation conversations in real-time and provides strategic advice to the user.

## Features

- **Real-Time Analysis**: Uses WebSocket to receive messages and send instant feedback.
- **Parallel Execution**: Runs three specialized prompts concurrently:
    1.  **Suspicion Analysis**: Detects bluffs, inconsistencies, and weaknesses.
    2.  **Suggestion Engine**: Proposes the next best tactical move.
    3.  **Fact Checker**: Extracts and verifies prices, specs, and history.
- **Unified Keyword System**: Fetches company-specific keywords (tactics, facts, context) from the backend API to ground the AI's advice.
- **Author Awareness**: Distinguishes between **User (Buyer)** and **Vendor (Seller)** to provide targeted advice.
- **Hint Saving**: Saves AI-generated hints to the database for future reference.
- **Conditional Responses**: The AI can choose to remain silent ("NO_RESPONSE") if no action is needed.
- **JSON Output**: Returns structured JSON responses for easy frontend integration.

## Architecture

- **Server**: Python WebSocket Server (Port `8767`).
- **AI Model**: Claude 3 Haiku (`anthropic.claude-3-haiku-20240307-v1:0`) via AWS Bedrock (`eu-central-1`).
- **Database**: Async MySQL connection (`aiomysql`) for saving history and hints.
- **Backend Integration**: Fetches keywords from `fast-api-hands` (`http://localhost:8000`).

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Database**:
    - Copy `dbcreds_template.py` to `dbcreds.py`.
    - Fill in your MySQL database credentials.

3.  **Configure AWS**:
    - Ensure you have AWS credentials configured (`~/.aws/credentials`) with access to Bedrock.

4.  **Run**:
    ```bash
    python3 main.py
    ```

## API

See [API.md](API.md) for details on the WebSocket protocol.
