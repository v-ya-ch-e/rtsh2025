# FastAPI Hands

**FastAPI Hands** is the backend API and data storage service for the `rtsh2025` project. It manages company data, conversations, documents, and the unified keyword system.

## Features

- **Company Management**: List companies (`GET /companies`).
- **Conversation Tracking**: Create new conversations (`POST /conversations`).
- **Unified Keyword System**:
    - `GET /companies/{id}/keywords`: Retrieve the consolidated keyword string for a company.
    - `POST /companies/{id}/keywords`: Update keywords.
- **Document Management**:
    - `POST /companies/{id}/documents`: Upload PDF/Doc files.
    - `GET /companies/{id}/documents`: List uploaded documents.
- **Legacy Storage**: Supports legacy `context` and `knowledge` file endpoints (migrated to keywords).

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Database**:
    - Ensure `dbcreds.py` is present (shared with `llama-connector` or created separately).

3.  **Run**:
    ```bash
    python3 main.py
    ```
    The server runs on `http://0.0.0.0:8000`.

## API Endpoints

### Companies
- `GET /companies`: List all companies.

### Conversations
- `POST /conversations`: Create a new conversation.
    - Body: `{"vendor_id": int}`

### Keywords (Unified Context)
- `GET /companies/{id}/keywords`: Get keywords.
- `POST /companies/{id}/keywords`: Save keywords.
    - Body: `string` (text/plain)

### Documents
- `GET /companies/{id}/documents`: List documents.
- `POST /companies/{id}/documents`: Upload document.
    - Form Data: `file`
