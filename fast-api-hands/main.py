from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import uvicorn
import dbcreds

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=dbcreds.DB_HOST,
            user=dbcreds.DB_USER,
            password=dbcreds.DB_PASSWORD,
            database=dbcreds.DB_NAME,
            port=dbcreds.DB_PORT
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to DB: {err}")
        return None

@app.get("/companies")
def get_companies():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM companies")
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database query error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

from pydantic import BaseModel

class KnowledgeBase(BaseModel):
    company_id: int
    content: str

@app.get("/knowledge/{company_id}")
def get_knowledge(company_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT content FROM knowledge_bases WHERE company_id = %s", (company_id,))
        result = cursor.fetchone()
        if result:
            return {"company_id": company_id, "content": result["content"]}
        else:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database query error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.post("/knowledge")
def create_or_update_knowledge(kb: KnowledgeBase):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge_bases (company_id, content) 
            VALUES (%s, %s) 
            ON DUPLICATE KEY UPDATE content = %s
        """, (kb.company_id, kb.content, kb.content))
        conn.commit()
        return {"message": "Knowledge base saved successfully", "company_id": kb.company_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

class ConversationCreate(BaseModel):
    vendor_id: int

@app.post("/conversations")
def create_conversation(conv: ConversationCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO conversations (vendor_id) VALUES (%s)", (conv.vendor_id,))
        conn.commit()
        new_id = cursor.lastrowid
        return {"id": new_id, "vendor_id": conv.vendor_id}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

from fastapi import UploadFile, File
import shutil
import os

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post("/companies/{company_id}/documents")
async def upload_document(company_id: int, file: UploadFile = File(...)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        file_path = os.path.join(UPLOAD_DIR, f"{company_id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO company_documents (company_id, filename, file_path) 
            VALUES (%s, %s, %s)
        """, (company_id, file.filename, file_path))
        conn.commit()
        
        return {"message": "File uploaded successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.get("/companies/{company_id}/documents")
def get_documents(company_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM company_documents WHERE company_id = %s", (company_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database query error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

import boto3
import json

# Initialize Bedrock Runtime Client
# Region: eu-central-1 (Frankfurt)
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='eu-central-1'
)

CLAUDE_SONNET_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

@app.get("/get_summary/{conv_id}")
def get_conversation_summary(conv_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        # Fetch all messages for the conversation
        cursor.execute("SELECT author, message FROM dialogs WHERE conv_id = %s ORDER BY message_id ASC", (conv_id,))
        rows = cursor.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        # Format conversation history
        history_str = ""
        for row in rows:
            history_str += f"{row['author'].upper()}: {row['message']}\n"
            
        # Construct prompt for Claude 3.5 Sonnet
        prompt = f"""You are an expert negotiator and analyst.
        
CONVERSATION HISTORY:
{history_str}

YOUR TASK:
Provide a comprehensive summary of this negotiation.
Include:
1. Key topics discussed.
2. Offers and counter-offers made.
3. The current state of the negotiation (agreed, stalled, ongoing).
4. Any specific tactical insights or warnings.

OUTPUT FORMAT:
Return a clear, well-structured summary in Markdown format. The output should be ready to show to the end user (with out any of your thoughts)
"""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": 0.5
        })
        
        response = bedrock_runtime.invoke_model(
            body=body,
            modelId=CLAUDE_SONNET_ID,
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        summary = response_body.get('content')[0].get('text')
        
        return {"conv_id": conv_id, "summary": summary}
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
