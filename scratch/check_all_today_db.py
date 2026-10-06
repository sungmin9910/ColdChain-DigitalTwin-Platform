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
        SELECT id, run_id, timestamp_str, created_at, lat, lng, speed, g_force, lux, temperature, humidity, status
        FROM sensor_data
        WHERE timestamp_str LIKE '2026-10-06%' OR created_at >= '2026-10-06 00:00:00'
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    print(f"Total 2026-10-06 rows in DB: {len(rows)}")
    for r in rows:
        print(f"ID:{r['id']} | run_id:{r['run_id']} | ts:{r['timestamp_str']} | created:{r['created_at']} | lat:{r['lat']:.5f} lng:{r['lng']:.5f} spd:{r['speed']} | status:{r['status']}")

conn.close()
