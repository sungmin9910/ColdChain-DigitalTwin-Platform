import sys
import os
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

DB_HOST = "15.165.68.30"
DB_USER = "admin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_NAME = "lab225"
DB_PORT = 3306

print(f"Testing AWS RDS connection for QR Scanner...")
print(f"Host: {DB_HOST}:{DB_PORT}, DB: {DB_NAME}, User: {DB_USER}")

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        charset="utf8mb4"
    )
    print("✅ DB 연결 성공!")
    
    with conn.cursor() as cursor:
        # 1. qr 테이블 상태 확인
        cursor.execute("SELECT COUNT(*) FROM qr")
        qr_cnt = cursor.fetchone()[0]
        print(f"• qr 테이블 총 레코드 수: {qr_cnt:,} 건")
        
        # 2. 최근 qr 레코드 3건 확인
        cursor.execute("SELECT id, Lo, FmID, FrT, Vt, created_at FROM qr ORDER BY id DESC LIMIT 3")
        recent_qr = cursor.fetchall()
        print("• 최근 QR 레코드:")
        for r in recent_qr:
            print(f"   ID: {r[0]} | 단계: {r[1]} | FmID: {r[2]} | 품종: {r[4]} | 일시: {r[5]}")
            
        # 3. 최신 센서 데이터(GPS/온습도) 조회 확인
        cursor.execute("SELECT id, lat, lng, temperature, humidity, created_at FROM sensor_data ORDER BY id DESC LIMIT 1")
        last_s = cursor.fetchone()
        if last_s:
            print(f"• 연동할 최신 센서 데이터: ID={last_s[0]} | GPS=({last_s[1]}, {last_s[2]}) | 온습도=({last_s[3]}°C, {last_s[4]}%)")
        else:
            print("• 센서 데이터가 비어 있습니다.")
            
    conn.close()
    print("\n✅ QR 스캐너 데이터베이스 파이프라인 검증 완료 (정상 동작 준비 완료)!")
    
except Exception as e:
    print(f"❌ DB 연결 에러: {e}")
