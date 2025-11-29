# FastAPI Hands

A simple FastAPI application to serve company data from a MySQL database.

## Features

- **Companies Endpoint**: `GET /companies` retrieves all companies from the database.

## Prerequisites

- Python 3.8+
- MySQL Database with a `companies` table.

## Installation

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Credentials**:
    Ensure `dbcreds.py` is present in the directory with the following variables:
    - `DB_HOST`
    - `DB_PORT`
    - `DB_USER`
    - `DB_PASSWORD`
    - `DB_NAME`

## Usage

1.  **Start the Server**:
    ```bash
    python3 main.py
    ```
    The server will start on `http://0.0.0.0:8000`.

2.  **Access the Endpoint**:
    Open your browser or use curl:
    ```bash
## Deployment

For detailed instructions on how to deploy this application to AWS EC2, please refer to [DEPLOYMENT.md](DEPLOYMENT.md).
