import toml
import pymysql

secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']
conn = pymysql.connect(host=cfg['MYSQL_HOST'], port=cfg.get('MYSQL_PORT', 3306), user=cfg['MYSQL_USER'], password=cfg['MYSQL_PASSWORD'], database=cfg['MYSQL_DATABASE'], cursorclass=pymysql.cursors.DictCursor)

with conn.cursor() as c:
    c.execute('SELECT COUNT(*), MIN(timestamp_str), MAX(timestamp_str), MIN(created_at), MAX(created_at) FROM sensor_data WHERE run_id = %s', ('run_20261002_080002_departure',))
    print('Departure Stats:', c.fetchone())
    
    # 올 때 데이터의 timestamp_str 및 created_at 확인
    c.execute('SELECT COUNT(*), MIN(timestamp_str), MAX(timestamp_str), MIN(created_at), MAX(created_at) FROM sensor_data WHERE run_id = %s', ('run_20261002_012518',))
    print('Return Stats:', c.fetchone())
