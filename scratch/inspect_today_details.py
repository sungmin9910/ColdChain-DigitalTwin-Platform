import toml
import pymysql

sec = toml.load(r'Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')['MySQL']
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
    print("=== Detailed inspection of today's records (2026-10-12) ===")
    
    # 1. Check run_id = '주행_2026-10-12_17시06분'
    cur.execute('''
        SELECT id, device, timestamp_str, created_at, temperature, humidity, lux, g_force, speed, lat, lng, status
        FROM sensor_data
        WHERE run_id LIKE '%17%06%'
        ORDER BY id ASC
    ''')
    rows_1706 = cur.fetchall()
    print(f"\n1. run_id '17:06' count: {len(rows_1706)}")
    if rows_1706:
        print(f"  First: {rows_1706[0]}")
        print(f"  Last:  {rows_1706[-1]}")
        
    # 2. Check run_id = '주행_2026-10-12_12시09분'
    cur.execute('''
        SELECT id, device, timestamp_str, created_at, temperature, humidity, lux, g_force, speed, lat, lng, status
        FROM sensor_data
        WHERE run_id LIKE '%12%09%'
        ORDER BY id ASC
    ''')
    rows_1209 = cur.fetchall()
    print(f"\n2. run_id '12:09' count: {len(rows_1209)}")
    for r in rows_1209[:5]:
        print(f"  Sample: id={r['id']} dev={r['device']} ts={r['timestamp_str']} created={r['created_at']} temp={r['temperature']} humi={r['humidity']} spd={r['speed']} g={r['g_force']} gps=({r['lat']},{r['lng']}) status={r['status']}")

    # 3. Check run_id = '주행_2026-10-12_12시08분'
    cur.execute('''
        SELECT id, device, timestamp_str, created_at, temperature, humidity, lux, g_force, speed, lat, lng, status
        FROM sensor_data
        WHERE run_id LIKE '%12%08%'
        ORDER BY id ASC
    ''')
    rows_1208 = cur.fetchall()
    print(f"\n3. run_id '12:08' count: {len(rows_1208)}")
    
    # Device breakdown of 12:08
    dev_1208 = {}
    for r in rows_1208:
        dev_1208[r['device']] = dev_1208.get(r['device'], 0) + 1
    print(f"  12:08 device breakdown: {dev_1208}")
    
    # Check anomalous records in 12:08
    bad_temp = [r for r in rows_1208 if r['temperature'] <= 0 or r['temperature'] > 40]
    bad_humi = [r for r in rows_1208 if r['humidity'] <= 0]
    print(f"  12:08 records with temp <= 0 or > 40: {len(bad_temp)}")
    for r in bad_temp[:5]:
        print(f"    Bad temp sample: id={r['id']} dev={r['device']} ts={r['timestamp_str']} temp={r['temperature']} humi={r['humidity']}")
    print(f"  12:08 records with humi <= 0: {len(bad_humi)}")
