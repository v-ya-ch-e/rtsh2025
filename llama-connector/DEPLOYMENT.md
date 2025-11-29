# AWS Deployment Guide

## Instance Recommendation
**Instance Type**: `t3.small` (2 vCPU, 2 GB RAM).
**OS**: Ubuntu Server 24.04 LTS.

## Deployment Steps

### 1. Create EC2 Instance
1.  Log in to AWS Console -> **EC2**.
2.  Click **Launch Instance**.
3.  **Name**: `Negotiation-Server`.
4.  **OS**: Ubuntu Server 24.04 LTS (x86).
5.  **Instance Type**: `t3.small`.
6.  **Key Pair**: Create new key pair (e.g., `negotiation-key`), download the `.pem` file.
7.  **Network Settings**:
    - Allow SSH traffic from **My IP**.
    - Allow Custom TCP traffic on port **8767** (WebSocket) from **Anywhere** (`0.0.0.0/0`).
8.  **Storage**: 20 GB gp3.
9.  Click **Launch Instance**.

### 2. Connect to Instance
```bash
chmod 400 negotiation-key.pem
ssh -i negotiation-key.pem ubuntu@<instance-public-ip>
```

### 3. Setup Environment
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv -y

# Install AWS CLI (for credentials)
sudo apt install awscli -y
```

### 4. Deploy Code
```bash
# Clone repo (or copy files)
git clone <your-repo-url>
cd llama-connector

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Credentials
1.  **AWS**: Run `aws configure` and enter your credentials.
2.  **Database**:
    ```bash
    cp dbcreds_template.py dbcreds.py
    nano dbcreds.py
    ```
    Fill in your RDS details.

### 6. Run as Service (Systemd)
We have provided a `llama-connector.service` file. You need to copy it to the systemd directory and update the paths if necessary.

1.  **Copy Service File**:
    ```bash
    sudo cp llama-connector.service /etc/systemd/system/
    ```

2.  **Edit Service File (if paths differ)**:
    ```bash
    sudo nano /etc/systemd/system/llama-connector.service
    ```
    *Ensure `WorkingDirectory` and `ExecStart` point to the correct locations.*

3.  **Enable and Start**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable llama-connector
    sudo systemctl start llama-connector
    ```

4.  **Check Status**:
    ```bash
    sudo systemctl status llama-connector
    ```

### 7. Accessing the Server
Your server is now running on `ws://<instance-public-ip>:8767`.
