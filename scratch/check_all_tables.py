import toml
import pymysql

sec = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')['MySQL']
conn = pymysql.connect(
    host=sec['MYSQL_HOST'],
    user=sec['MYSQL_USER'],
    password=sec['MYSQL_PASSWORD'],
    database=sec['MYSQL_DATABASE'],
    port=sec.get('MYSQL_PORT', 3306),
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("SHOW TABLES")
    tables = [list(r.values())[0] for r in cur.fetchall()]
    print(f"Total tables: {len(tables)}")
    for t in tables:
        cur.execute(f"SELECT COUNT(*) as c FROM `{t}`")
        cnt = cur.fetchone()['c']
        print(f"  - {t}: {cnt} rows")
conn.close()
