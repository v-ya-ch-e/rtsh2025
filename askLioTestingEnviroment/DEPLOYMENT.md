# Deployment Guide: Simulation Environment

This guide explains how to deploy the AskLio Simulation Environment on AWS EC2.

## Prerequisites

- An AWS EC2 instance (Ubuntu 24.04 recommended).
- **Llama Connector** deployed and running on the same instance (Port 8767).
- Python 3.10+ installed.

## Steps

### 1. Setup Directory
Assuming you have cloned the repository to `~/rtsh2025`:

```bash
cd ~/rtsh2025/askLioTestingEnviroment
```

### 2. Install Dependencies
Create a virtual environment (optional but recommended) or install globally:

```bash
# Option A: Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option B: Global Install
pip3 install -r requirements.txt --break-system-packages
```

### 3. Configure Service
We use `systemd` to run the simulation server in the background.

1.  Edit the `simulation-env.service` file to match your paths (check `User` and `WorkingDirectory`).
2.  Copy the service file:
    ```bash
    sudo cp simulation-env.service /etc/systemd/system/
    ```
3.  Reload systemd and start the service:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable simulation-env
    sudo systemctl start simulation-env
    ```
4.  Check status:
    ```bash
    sudo systemctl status simulation-env
    ```

### 4. Accessing the Simulation
Since the frontend is a static HTML file that connects to the WebSocket, you have two options:

#### Option A: Serve HTML via Nginx (Recommended)
1.  Install Nginx: `sudo apt install nginx`
2.  Copy `index.html` to `/var/www/html/simulation.html`.
3.  Access via `http://<your-ec2-ip>/simulation.html`.
    *Note: You must edit `index.html` to point the WebSocket to `ws://<your-ec2-ip>:8768` instead of `localhost`.*

#### Option B: Local HTML File
1.  Download `index.html` to your local machine.
2.  Edit line 42 to point to your EC2 IP:
    ```javascript
    const ws = new WebSocket("ws://<your-ec2-ip>:8768");
    ```
3.  Open the file in your browser.

## Security Note
Ensure your EC2 Security Group allows inbound traffic on port **8768** (Custom TCP).
