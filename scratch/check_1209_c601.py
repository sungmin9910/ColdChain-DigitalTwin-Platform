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
        SELECT id, device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, created_at 
        FROM sensor_data 
        WHERE run_id = '주행_2026-10-12_12시09분' AND device = 'carrier-c6-01'
        ORDER BY id ASC
    """)
    rows = cur.fetchall()
    print(f"carrier-c6-01 in 12:09: {len(rows)}")
    for r in rows:
        print(f"id={r['id']} ts={r['timestamp_str']} t={r['temperature']} h={r['humidity']} spd={r['speed']} g={r['g_force']} lat={r['lat']}")
conn.close()
