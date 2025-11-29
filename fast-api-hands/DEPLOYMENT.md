# AWS Deployment Guide for FastAPI Hands

## Instance Recommendation
You can run this on the same instance as `llama-connector` (`t3.small`) or a separate one.
**Port**: This application runs on port **8000**. Ensure this port is open in your Security Group if you want external access.

## Deployment Steps

### 1. Deploy Code
Assuming you are on the EC2 instance:

```bash
# Clone repo (if not already done)
git clone <your-repo-url>
cd fast-api-hands

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials
Ensure `dbcreds.py` is present in the `fast-api-hands` directory. You can copy it from `llama-connector` if they share the DB.

```bash
cp ../llama-connector/dbcreds.py .
```

### 3. Run as Service (Systemd)
We have provided a `fast-api-hands.service` file.

1.  **Copy Service File**:
    ```bash
    sudo cp fast-api-hands.service /etc/systemd/system/
    ```

2.  **Edit Service File (if paths differ)**:
    ```bash
    sudo nano /etc/systemd/system/fast-api-hands.service
    ```
    *Ensure `WorkingDirectory` and `ExecStart` point to the correct locations.*

3.  **Enable and Start**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable fast-api-hands
    sudo systemctl start fast-api-hands
    ```

4.  **Check Status**:
    ```bash
    sudo systemctl status fast-api-hands
    ```

### 4. Accessing the Endpoint
Your API is now running on `http://<instance-public-ip>:8000/companies`.
