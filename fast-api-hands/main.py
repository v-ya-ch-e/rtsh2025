from fastapi import FastAPI, HTTPException
import mysql.connector
import uvicorn
import dbcreds

app = FastAPI()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
