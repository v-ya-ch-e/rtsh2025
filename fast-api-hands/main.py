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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
