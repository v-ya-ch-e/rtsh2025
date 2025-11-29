# Llama Connector API Documentation

## WebSocket Endpoint
**URL**: `ws://<server-ip>:8767`

## Message Protocol

### Request (Client -> Server)
The client sends a JSON object with the following fields:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `conv_id` | Integer | Yes | Unique identifier for the conversation. |
| `text` | String | Yes | The text message to analyze. |
| `company_id` | Integer | No | ID of the company for RAG context (default: 1). |
| `author` | String | No | Who sent the text: `"user"` or `"opponent"` (default: `"user"`). |

**Example:**
```json
{
  "conv_id": 123,
  "text": "We cannot go lower than $500.",
  "company_id": 1,
  "author": "opponent"
}
```

### Response (Server -> Client)
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

## Error Handling
If the request is invalid or an error occurs, the server may return an error message or simply log the error. Ensure `conv_id` and `text` are always provided.
