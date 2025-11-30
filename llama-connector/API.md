# Llama Connector API

The Llama Connector exposes a WebSocket API on port `8767`.

## Connection

**URL**: `ws://<server_ip>:8767`

## Messages

### Request Format (Client -> Server)

Send a JSON object with the following fields:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `conv_id` | Integer | Yes | Unique identifier for the conversation. |
| `text` | String | Yes | The text message to analyze. |
| `company_id` | Integer | No | ID of the company for keyword retrieval (default: 1). |
| `author` | String | No | Who sent the text: `"user"` (Buyer) or `"vendor"` (Seller) (default: `"user"`). |

**Example:**
```json
{
  "conv_id": 123,
  "text": "We can offer a 5% discount if you sign today.",
  "company_id": 1,
  "author": "vendor"
}
```

### Response Format (Server -> Client)

The server returns a JSON object with the AI's analysis and advice.

| Field | Type | Description |
| :--- | :--- | :--- |
| `MESSAGE_COLOR` | String | Color code for the advice: `"red"` (Warning), `"green"` (Go/Good), `"blue"` (Info), `"yellow"` (Caution). |
| `MESSAGE` | String | The advice text to display to the user. Max 50 words. |

**Example:**
```json
{
  "MESSAGE_COLOR": "red",
  "MESSAGE": "Decision: BLUFF. They are using time pressure ('sign today') to force a decision. Counter-anchor: Ask for 15% off or walk away."
}
```

**Note**: If the AI determines no action is needed, it will not send a response (or internal logic handles "NO_RESPONSE").
