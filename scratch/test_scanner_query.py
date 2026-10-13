import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host="15.165.68.30",
    user="admin",
    password="12345678",
    database="lab225",
    port=3306,
    charset="utf8mb4"
)

with conn.cursor() as c:
    c.execute("SELECT lat, lng, temperature, humidity, created_at FROM lab225.sensor_data ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    print("Latest sensor_data record:", row)

    c.execute("SELECT Lo, FmID, APC_AD, Lat, lon FROM lab225.qr ORDER BY HD DESC LIMIT 3")
    qrs = c.fetchall()
    print("Latest qr records:")
    for q in qrs:
        print(" ", q)

conn.close()
print("Scanner queries are 100% compatible with DB!")
