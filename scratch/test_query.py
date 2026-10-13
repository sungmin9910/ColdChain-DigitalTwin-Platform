import pymysql

conn = pymysql.connect(host='15.165.68.30', user='admin', password='12345678', database='lab225', port=3306)
with conn.cursor() as cur:
    cur.execute("SELECT Lo FROM lab225.qr WHERE FmID = '77' ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    print('Query result for FmID 77:', row)
conn.close()
