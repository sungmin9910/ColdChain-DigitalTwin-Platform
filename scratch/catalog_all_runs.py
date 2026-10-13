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
    cur.execute('''
        SELECT 
            run_id,
            GROUP_CONCAT(DISTINCT device ORDER BY device SEPARATOR ', ') as devices,
            COUNT(*) as total_cnt,
            COUNT(CASE WHEN lat != 0 AND lat IS NOT NULL THEN 1 END) as gps_cnt,
            MIN(timestamp_str) as min_ts,
            MAX(timestamp_str) as max_ts,
            MIN(created_at) as min_created,
            MAX(created_at) as max_created,
            ROUND(MIN(temperature), 1) as min_t,
            ROUND(MAX(temperature), 1) as max_t,
            ROUND(MIN(humidity), 1) as min_h,
            ROUND(MAX(humidity), 1) as max_h,
            ROUND(MAX(speed), 1) as max_spd,
            ROUND(MAX(g_force), 2) as max_g
        FROM sensor_data
        GROUP BY run_id
        ORDER BY min_created DESC
    ''')
    rows = cur.fetchall()
    print(f"Total distinct run_ids: {len(rows)}")
    print("-" * 120)
    for r in rows:
        print(f"[{r['run_id']}]")
        print(f"    devices: {r['devices']} | total: {r['total_cnt']} (GPS: {r['gps_cnt']}) | speed_max: {r['max_spd']} km/h")
        print(f"    created: {r['min_created']} ~ {r['max_created']} | ts: {r['min_ts']} ~ {r['max_ts']}")
        print(f"    temp: {r['min_t']}~{r['max_t']}°C | humi: {r['min_h']}~{r['max_h']}% | max_g: {r['max_g']}G")
        print("-" * 120)
