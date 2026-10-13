import toml
import pymysql

sec = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')['MySQL']
conn = pymysql.connect(
    host=sec['MYSQL_HOST'],
    port=sec.get('MYSQL_PORT', 3306),
    user=sec['MYSQL_USER'],
    password=sec['MYSQL_PASSWORD'],
    database=sec['MYSQL_DATABASE'],
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("""
        SELECT id, device, timestamp_str, temperature, humidity, speed, g_force, lat, lng 
        FROM sensor_data 
        WHERE run_id = '주행_2026-10-12_12시08분' AND (temperature <= 0 OR humidity <= 0)
    """)
    rows = cur.fetchall()
    print(f"Dropout rows in 12:08 run: {len(rows)}")
    for r in rows:
        print(f"  id={r['id']} dev={r['device']} ts={r['timestamp_str']} temp={r['temperature']} humi={r['humidity']} spd={r['speed']}")
conn.close()
