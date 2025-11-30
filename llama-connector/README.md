# Llama Connector (Negotiation Assistant)

This project implements a real-time negotiation assistant server using AWS Bedrock (Claude 3 Haiku) and WebSockets. It analyzes conversation text in parallel to detect bluffs, suggest next moves, and find relevant facts, then aggregates the results into a final recommendation.

## Features

- **WebSocket Server**: Listens for incoming conversation text.
- **Parallel Processing**: Uses `asyncio` to run three analysis prompts concurrently on AWS Bedrock.
- **Async DB Saving**: Saves messages to a MySQL database in the background without blocking the response.
- **JSON Output**: Returns structured JSON responses (`MESSAGE_COLOR`, `MESSAGE`).
- **Retry Logic**: Automatically retries if the LLM fails to generate valid JSON.
- **Author Awareness**: Distinguishes between **User (Buyer)** and **Vendor (Seller)** to provide targeted advice.
- **Dynamic Knowledge Base**: Fetches company-specific tactics and facts from the database.
- **Conversation Tracking**: Supports creating and tracking conversations via a dedicated API.

## Prerequisites

- Python 3.8+
- AWS Account with Bedrock access (Claude 3 Haiku enabled in `eu-central-1`).
- MySQL Database.
- **FastAPI Hands**: Companion service for managing company data and conversations.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd llama-connector
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **AWS Credentials**:
    Ensure you have configured your AWS credentials. You can use the AWS CLI:
    ```bash
    aws configure
    ```
    Or set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION=eu-central-1`.

2.  **Database Credentials**:
    Copy the template and fill in your details:
    ```bash
    cp dbcreds_template.py dbcreds.py
    ```
    Edit `dbcreds.py` with your MySQL host, user, password, and database name.

## Usage

1.  **Start the Server**:
    ```bash
    python3 main.py
    ```
    The server will start on `ws://localhost:8767`.

2.  **Run the Test Client**:
    ```bash
    python3 test_client.py
    ```
    This sends a sample message from `text_block1` (or a default string) and prints the JSON response.

## Deployment

For detailed instructions on how to deploy this application to AWS EC2, please refer to [DEPLOYMENT.md](DEPLOYMENT.md).

## Protocol

**Request (JSON)**:
```json
{
  "conv_id": 123,
  "text": "I want to ensure you, that our product is great...",
  "company_id": 1,
  "author": "vendor" 
}
```
*Note: `author` can be `"user"` (Buyer) or `"vendor"` (Seller).*

**Response (JSON)**:
```json
{
  "MESSAGE_COLOR": "red",
  "MESSAGE": "The claim lacks specific evidence..."
}
```
