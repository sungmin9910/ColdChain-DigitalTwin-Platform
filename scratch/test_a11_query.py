import pymysql

conn = pymysql.connect(host='15.165.68.30', user='admin', password='12345678', database='lab225', port=3306)
with conn.cursor() as cur:
    query = """
        SELECT 'A11', Q.AC, Q.FmID, Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.StD, Q.Rp, Q.APC_AD, NOW(), S.lat, S.lng 
        FROM lab225.qr Q, (SELECT lat, lng, temperature, humidity FROM lab225.sensor_data ORDER BY id DESC LIMIT 1) S 
        WHERE Q.FmID = '77' AND Q.APC_AD IS NOT NULL ORDER BY Q.APC_AD DESC LIMIT 1;
    """
    cur.execute(query)
    row = cur.fetchone()
    print("A11 query preview:", row)
conn.close()
