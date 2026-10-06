import pymysql

conn = pymysql.connect(
    host="labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com",
    port=3306,
    user="admin",
    password="12345678",
    database="lab225",
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cursor:
    cursor.execute("""
        SELECT id, run_id, timestamp_str, created_at, temperature, humidity, lux, status
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    print("=== Latest 20 Records in DB ===")
    for r in rows:
        print(f"ID:{r['id']} | run:{r['run_id']} | ts:{r['timestamp_str']} | created:{r['created_at']} | temp:{r['temperature']:.2f}°C humi:{r['humidity']:.1f}% lux:{r['lux']:.1f}")

conn.close()
