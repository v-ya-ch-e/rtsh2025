# Llama Connector & Companion API Documentation

## 1. WebSocket Endpoint (Llama Connector)
**URL**: `ws://<server-ip>:8767`

### Message Protocol

#### Request (Client -> Server)
The client sends a JSON object with the following fields:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `conv_id` | Integer | Yes | Unique identifier for the conversation. |
| `text` | String | Yes | The text message to analyze. |
| `company_id` | Integer | No | ID of the company for RAG context (default: 1). |
| `author` | String | No | Who sent the text: `"user"` (Buyer) or `"vendor"` (Seller) (default: `"user"`). |

**Example:**
```json
{
  "conv_id": 123,
  "text": "We cannot go lower than $500.",
  "company_id": 1,
  "author": "vendor"
}
```

#### Response (Server -> Client)
The server responds with a JSON object containing the analysis and recommendation.

| Field | Type | Description |
| :--- | :--- | :--- |
| `MESSAGE_COLOR` | String | Color code for the message (e.g., "red", "green", "yellow"). |
| `MESSAGE` | String | The analysis or recommendation text. |

**Example:**
```json
{
  "MESSAGE_COLOR": "red",
  "MESSAGE": "The opponent is likely bluffing. Ask for a breakdown of costs."
}
```

## 2. REST API (FastAPI Hands)
**URL**: `http://<server-ip>:8000`

### Endpoints

#### `GET /companies`
Returns a list of all companies.

#### `POST /conversations`
Creates a new conversation.
- **Body**: `{"vendor_id": int}`
- **Response**: `{"id": int, "vendor_id": int}`

#### `GET /knowledge/{company_id}`
Retrieves the knowledge base for a specific company.

#### `POST /knowledge`
Creates or updates a knowledge base.
- **Body**: `{"company_id": int, "content": "string"}`
