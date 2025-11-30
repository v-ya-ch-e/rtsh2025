# AWS Deployment Guide

This guide covers the deployment of the entire `rtsh2025` repository, including:
1.  **Llama Connector**: WebSocket server for negotiation assistance (with RAG).
2.  **FastAPI Hands**: API for company data.
3.  **RAG Helper**: Context retrieval system.

## Instance Recommendation
**Instance Type**: `t3.small` (2 vCPU, 2 GB RAM) or `t3.medium` if you expect heavy load.
**OS**: Ubuntu Server 24.04 LTS.

## Deployment Steps

### 1. Create EC2 Instance
1.  Log in to AWS Console -> **EC2**.
2.  Click **Launch Instance**.
3.  **Name**: `Negotiation-Server`.
4.  **OS**: Ubuntu Server 24.04 LTS (x86).
5.  **Instance Type**: `t3.small`.
6.  **Key Pair**: Create new or use existing.
7.  **Network Settings**:
    - Allow SSH (22) from **My IP**.
    - Allow Custom TCP (8767) for WebSocket from **Anywhere**.
    - Allow Custom TCP (8000) for FastAPI from **Anywhere**.
8.  **Storage**: 20 GB gp3.
9.  Click **Launch Instance**.

### 2. Connect to Instance
```bash
ssh -i key.pem ubuntu@<public-ip>
```

### 3. Setup Environment
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv git -y

# Install AWS CLI
sudo apt install awscli -y
```

### 4. Deploy Code
**Important**: Clone the *entire* repository to ensure `llama-connector` can access `RAG_helper`.

```bash
# Clone repo
git clone <your-repo-url> rtsh2025
cd rtsh2025
```

### 5. Setup Llama Connector (WebSocket + RAG)
```bash
cd llama-connector

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS Credentials
aws configure

# Configure DB Credentials
cp dbcreds_template.py dbcreds.py
nano dbcreds.py  # Fill in MySQL details

# Configure OpenAI Key for RAG
# Option A: Env Var (Recommended)
export OPENAI_API_KEY="sk-..."
# Option B: Cred file
echo "sk-..." > ../RAG_helper/cred
```

### 6. Setup FastAPI Hands (Company API)
You can use the same venv or a new one. Here we use a new one for isolation.

```bash
cd ../fast-api-hands

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure DB Credentials
cp ../llama-connector/dbcreds.py .
```

### 7. Run as Services (Systemd)

#### Llama Connector Service
1.  Edit `llama-connector.service` to match paths (e.g., `/home/ubuntu/rtsh2025/llama-connector`).
2.  Copy and start:
    ```bash
    sudo cp llama-connector.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable llama-connector
    sudo systemctl start llama-connector
    ```

#### FastAPI Service
1.  Edit `fast-api-hands.service` to match paths (e.g., `/home/ubuntu/rtsh2025/fast-api-hands`).
2.  Copy and start:
    ```bash
    sudo cp fast-api-hands.service /etc/systemd/system/
    sudo systemctl enable fast-api-hands
    sudo systemctl start fast-api-hands
    ```

### 8. Verification
- **WebSocket**: `ws://<public-ip>:8767`
- **API**: `http://<public-ip>:8000/companies`
