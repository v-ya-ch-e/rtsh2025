# Sekundant - Llama Connector Deployment Guide

## Prerequisites

- **Python 3.8+**
- **AWS Account** with Bedrock access (Claude 3 Haiku enabled in `eu-central-1`).
- **MySQL Database**.

## Installation

1.  **Clone Repository**:
    ```bash
    git clone <repo_url>
    cd llama-connector
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    - **Database**: Create `dbcreds.py` from `dbcreds_template.py` and add your credentials.
    - **AWS**: Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set in your environment or `~/.aws/credentials`.

## Running the Service

It is recommended to run the service using `systemd` for production.

### Systemd Service File (`/etc/systemd/system/llama-connector.service`)

```ini
[Unit]
Description=Sekundant Llama Connector WebSocket Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/rtsh2025/llama-connector
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable llama-connector
sudo systemctl start llama-connector
```
