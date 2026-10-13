import toml
import pymysql

secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']
conn = pymysql.connect(host=cfg['MYSQL_HOST'], port=cfg.get('MYSQL_PORT', 3306), user=cfg['MYSQL_USER'], password=cfg['MYSQL_PASSWORD'], database=cfg['MYSQL_DATABASE'])

with conn.cursor() as c:
    c.execute("DELETE FROM sensor_data WHERE run_id LIKE 'run_20261002_06%'")
    conn.commit()
    print("Deleted 06xx junk records:", c.rowcount)
conn.close()
