import pymysql

conn = pymysql.connect(host='15.165.68.30', user='admin', password='12345678', database='lab225', port=3306)
with conn.cursor() as cur:
    cur.execute("SELECT id, FmID, Lo, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, APC_OP FROM qr WHERE FmID = '77' ORDER BY id DESC LIMIT 5;")
    rows = cur.fetchall()
    print("=== Current records for FmID 77 ===")
    for r in rows:
        print(r)
conn.close()
