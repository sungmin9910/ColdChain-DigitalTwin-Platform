import json
import toml
import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/carrier02_dump_1017.jsonl', 'r', encoding='utf-8') as f:
    recs = [json.loads(l) for l in f if l.strip()]

print(f"Total dumped records: {len(recs)}")

if recs:
    ts_list = [r.get('timestamp_str') for r in recs]
    print(f"Start Timestamp: {ts_list[0]}")
    print(f"End Timestamp: {ts_list[-1]}")
    
    # Analyze metrics
    temps = [float(r['temperature']) for r in recs if float(r.get('temperature', 0)) > 0]
    humis = [float(r['humidity']) for r in recs if float(r.get('humidity', 0)) > 0]
    luxs = [float(r['lux']) for r in recs]
    g_forces = [float(r['g_force']) for r in recs]
    gps_recs = [r for r in recs if float(r.get('lat', 0)) > 0]
    speeds = [float(r['speed']) for r in gps_recs]
    
    if temps:
        print(f"Temperature: {min(temps):.2f}C ~ {max(temps):.2f}C (Avg: {sum(temps)/len(temps):.2f}C)")
    if humis:
        print(f"Humidity: {min(humis):.2f}% ~ {max(humis):.2f}% (Avg: {sum(humis)/len(humis):.2f}%)")
    if luxs:
        print(f"Lux: {min(luxs):.1f} ~ {max(luxs):.1f} lx")
    if g_forces:
        print(f"Max G-force: {max(g_forces):.2f} G")
        
    print(f"GPS Records with Fix: {len(gps_recs)}")
    if gps_recs:
        print(f"Max Speed: {max(speeds):.1f} km/h")
        print(f"Origin GPS: ({gps_recs[0]['lat']}, {gps_recs[0]['lng']})")
        print(f"End GPS: ({gps_recs[-1]['lat']}, {gps_recs[-1]['lng']})")
        
    shocks = [r for r in recs if float(r.get('g_force', 1.0)) >= 1.8]
    print(f"Shock events (>= 1.8G): {len(shocks)}")
    for s in shocks[:5]:
        print(f"  - [{s['timestamp_str']}] {s['g_force']}G | status: {s.get('status')}")

# Check MySQL DB
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
    cur.execute("SELECT count(*) as cnt FROM sensor_data WHERE device='carrier-c6-02' AND timestamp_str >= '2026-10-17 00:00:00'")
    cnt_today = cur.fetchone()['cnt']
    print(f"\n[MySQL DB Status] carrier-c6-02 records in DB today (2026-10-17): {cnt_today} rows")
    
    cur.execute("SELECT run_id, count(*) as cnt, min(timestamp_str) as t_start, max(timestamp_str) as t_end FROM sensor_data WHERE device='carrier-c6-02' GROUP BY run_id ORDER BY max(id) DESC LIMIT 5")
    rows = cur.fetchall()
    print("Recent sessions in DB:")
    for r in rows:
        print(r)

conn.close()
