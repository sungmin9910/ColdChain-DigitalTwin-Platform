import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = "15.165.68.30"
DB_USER = "admin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_NAME = "lab225"
DB_PORT = 3306

def check_schema():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_NAME, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("DESCRIBE qr")
        columns = cursor.fetchall()
        print("Table 'qr' structure:")
        for col in columns:
            print(col)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
