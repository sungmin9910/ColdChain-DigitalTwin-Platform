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
    cur.execute("SELECT timestamp_str, temperature, humidity, g_force FROM sensor_data WHERE run_id = '주행_2026-10-12_12시08분' AND device = 'carrier-c6-01'")
    r1208 = {f"{r['timestamp_str']}_{r['temperature']}_{r['humidity']}": r for r in cur.fetchall()}
    
    cur.execute("SELECT id, timestamp_str, temperature, humidity, g_force FROM sensor_data WHERE run_id = '주행_2026-10-12_12시09분' AND device = 'carrier-c6-01'")
    r1209 = cur.fetchall()
    
    dup_cnt = 0
    new_cnt = 0
    for r in r1209:
        k = f"{r['timestamp_str']}_{r['temperature']}_{r['humidity']}"
        if k in r1208:
            dup_cnt += 1
            print(f"DUPLICATE: id={r['id']} ts={r['timestamp_str']} t={r['temperature']}")
        else:
            new_cnt += 1
            print(f"UNIQUE IN 12:09: id={r['id']} ts={r['timestamp_str']} t={r['temperature']} h={r['humidity']}")
    print(f"Total in 12:09: {len(r1209)} -> Duplicates: {dup_cnt}, Unique: {new_cnt}")
conn.close()
