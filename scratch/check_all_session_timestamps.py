import pymysql, toml, pandas as pd
secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']
conn = pymysql.connect(host=cfg['MYSQL_HOST'], user=cfg['MYSQL_USER'], password=cfg['MYSQL_PASSWORD'], database=cfg['MYSQL_DATABASE'], port=cfg.get('MYSQL_PORT', 3306), charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

with conn.cursor() as cur:
    for run_name in ['run_20261002_080002_departure', 'run_20261002_103710_return', 'run_20261001_065739', 'korea_30km_test']:
        cur.execute("SELECT id, timestamp_str, created_at FROM sensor_data WHERE run_id = %s ORDER BY id ASC", (run_name,))
        rows = cur.fetchall()
        print(f"=== {run_name} (Total {len(rows)}) ===")
        if rows:
            print("  First 3:", [(r['id'], r['timestamp_str'], str(r['created_at'])) for r in rows[:3]])
            print("  Last 3:", [(r['id'], r['timestamp_str'], str(r['created_at'])) for r in rows[-3:]])
            # Check for 2026-10-01 00:00:00 or weird timestamps
            weird = [r for r in rows if str(r['timestamp_str']).startswith('2026-10-01 00:00') or str(r['timestamp_str']).startswith('1970') or '00:00:00' in str(r['timestamp_str'])]
            print(f"  Weird timestamps count: {len(weird)}")
            if weird:
                print("  Weird sample:", [(r['id'], r['timestamp_str'], str(r['created_at'])) for r in weird[:5]])
