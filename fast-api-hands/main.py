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
import json

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


from fastapi import Body

STORAGE_DIR = "storage"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def get_company_storage_path(company_id: int):
    path = os.path.join(STORAGE_DIR, "companies", str(company_id))
    if not os.path.exists(path):
        os.makedirs(path)
    return path

@app.get("/companies/{company_id}/context")
def get_company_context(company_id: int):
    path = os.path.join(get_company_storage_path(company_id), "context.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return {"content": f.read()}
    return {"content": ""}

@app.post("/companies/{company_id}/context")
def save_company_context(company_id: int, content: str = Body(..., media_type="text/plain")):
    path = os.path.join(get_company_storage_path(company_id), "context.txt")
    with open(path, "w") as f:
        f.write(content)
    return {"message": "Context saved"}

@app.get("/companies/{company_id}/knowledge_file")
def get_company_knowledge_file(company_id: int):
    path = os.path.join(get_company_storage_path(company_id), "knowledge.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return {"content": f.read()}
    return {"content": ""}

@app.post("/companies/{company_id}/knowledge_file")
def save_company_knowledge_file(company_id: int, content: str = Body(..., media_type="text/plain")):
    path = os.path.join(get_company_storage_path(company_id), "knowledge.txt")
    with open(path, "w") as f:
        f.write(content)
    return {"message": "Knowledge saved"}

KEYWORDS_FILE = os.path.join(STORAGE_DIR, "all_keywords.json")

def get_all_keywords():
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_all_keywords(data):
    with open(KEYWORDS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/companies/{company_id}/keywords")
def get_company_keywords(company_id: int):
    data = get_all_keywords()
    return {"keywords": data.get(str(company_id), "")}

@app.post("/companies/{company_id}/keywords")
def save_company_keywords(company_id: int, keywords: str = Body(..., media_type="text/plain")):
    data = get_all_keywords()
    data[str(company_id)] = keywords.strip()
    save_all_keywords(data)
    return {"message": "Keywords saved"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
