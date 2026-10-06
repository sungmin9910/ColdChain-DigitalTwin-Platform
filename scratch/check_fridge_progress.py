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
        SELECT COUNT(*) as cnt, MIN(timestamp_str) as start_ts, MAX(timestamp_str) as end_ts,
               MAX(temperature) as max_temp, MIN(temperature) as min_temp
        FROM sensor_data
        WHERE created_at >= '2026-10-06 12:45:00'
    """)
    stat = cursor.fetchone()
    print("=== Fridge Experiment Stats ===")
    print(stat)

    cursor.execute("""
        SELECT id, timestamp_str, temperature, humidity, lux
        FROM sensor_data
        WHERE created_at >= '2026-10-06 12:45:00'
        ORDER BY id DESC
        LIMIT 5
    """)
    latest = cursor.fetchall()
    print("\n=== Latest 5 records ===")
    for row in latest:
        print(row)

conn.close()
