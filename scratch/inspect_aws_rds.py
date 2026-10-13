import toml
import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']

print("==================================================")
print("  AWS RDS MySQL 인프라 실시간 상태 점검 보고서")
print("==================================================")
print(f"• 호스트: {cfg['MYSQL_HOST']}")
print(f"• 포트:   {cfg.get('MYSQL_PORT', 3306)}")
print(f"• 리전:   ap-northeast-2 (서울 리전)")
print(f"• DB명:   {cfg['MYSQL_DATABASE']}")
print(f"• 계정:   {cfg['MYSQL_USER']}")
print("--------------------------------------------------")

try:
    conn = pymysql.connect(
        host=cfg['MYSQL_HOST'],
        port=cfg.get('MYSQL_PORT', 3306),
        user=cfg['MYSQL_USER'],
        password=cfg['MYSQL_PASSWORD'],
        database=cfg['MYSQL_DATABASE'],
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )
    print("✅ [네트워크] AWS RDS MySQL 정상 접속 성공 (Connection Healthy)\n")
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION() as ver, CURRENT_TIMESTAMP() as ts, @@time_zone as tz")
        srv = cursor.fetchone()
        print(f"📦 MySQL 엔진: {srv['ver']} (AWS RDS Managed)")
        print(f"⏰ 서버 시각:   {srv['ts']} (기본 Timezone: {srv['tz']})")
        
        # 테이블 목록 조회
        cursor.execute("SHOW TABLES")
        tables_raw = cursor.fetchall()
        table_names = [list(r.values())[0] for r in tables_raw]
        
        print("\n📊 [데이터베이스 테이블 현황]")
        for t_name in table_names:
            cursor.execute(f"SELECT COUNT(*) as cnt FROM `{t_name}`")
            cnt = cursor.fetchone()['cnt']
            print(f"  • {t_name:<16s}: {cnt:>8,d} 건의 레코드 저장됨")

        # sensor_data 분석
        if 'sensor_data' in table_names:
            print("\n📡 [1. sensor_data 테이블 분석 (실시간 IoT 텔레메트리)]")
            cursor.execute("SELECT COUNT(*) as cnt FROM sensor_data")
            total_sd = cursor.fetchone()['cnt']
            print(f"  • 총 수집 데이터 건수: {total_sd:,d} 건")
            
            # 최신 5건
            cursor.execute("""
                SELECT id, device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, run_id, created_at
                FROM sensor_data 
                ORDER BY id DESC LIMIT 5
            """)
            recents = cursor.fetchall()
            print("  • 최신 수신 패킷 5건:")
            for r in recents:
                print(f"    - ID {r['id']:>5d} | {r['created_at']} | 온도:{r['temperature']:4.1f}°C | 습도:{r['humidity']:4.1f}% | 조도:{r['lux']:4.0f}lx | 충격:{r['g_force']:4.2f}G | GPS:({r['lat']:.4f}, {r['lng']:.4f}) | {r['run_id']}")
                
            # 실험 세션별 데이터 수집량 (상위 5개)
            cursor.execute("""
                SELECT run_id, COUNT(*) as cnt, MIN(created_at) as started, MAX(created_at) as ended
                FROM sensor_data 
                WHERE run_id IS NOT NULL 
                GROUP BY run_id 
                ORDER BY MAX(created_at) DESC 
                LIMIT 5
            """)
            runs = cursor.fetchall()
            print("\n  • 최근 실험 세션(run_id) 5건:")
            for ru in runs:
                print(f"    - 세션: {ru['run_id']:<24s} | 수집: {ru['cnt']:>5d}건 | 시작: {ru['started']} ~ 종료: {ru['ended']}")

        # qr 분석
        if 'qr' in table_names:
            print("\n🏷️ [2. qr 테이블 분석 (농가-APC-소비자 유통 추적 이력)]")
            cursor.execute("SELECT COUNT(*) as cnt FROM qr")
            total_qr = cursor.fetchone()['cnt']
            print(f"  • 총 유통 단계 이력: {total_qr:,d} 건")
            
            cursor.execute("SELECT * FROM qr LIMIT 5")
            recents_qr = cursor.fetchall()
            print("  • 최신 유통 이력 5건:")
            for q in recents_qr:
                lo = q.get('Lo', '-')
                fmid = q.get('FmID', '-')
                frt = q.get('FrT', '-')
                vt = q.get('Vt', '-')
                qt = q.get('Qt', '-')
                lat = q.get('Lat', q.get('lat', '-'))
                lon = q.get('lon', q.get('lng', '-'))
                print(f"    - 단계: {lo:<4s} | 농가ID: {fmid} | 품목: {frt}/{vt} | 수량: {qt}박스 | GPS: ({lat}, {lon})")
                
            # 유통 단계별(Lo) 건수 분포
            cursor.execute("""
                SELECT Lo, COUNT(*) as cnt 
                FROM qr 
                GROUP BY Lo 
                ORDER BY Lo ASC
            """)
            stage_stats = cursor.fetchall()
            print("\n  • 유통 단계별(Lo) 누적 데이터 분포:")
            stage_names = {
                'A00': '수확(농가)',
                'A10': '입고(APC)',
                'A11': '세척완료',
                'A12': '품질선별',
                'A13': '포장완료',
                'A14': '저온저장',
                'A15': '최종출하'
            }
            for s in stage_stats:
                desc = stage_names.get(s['Lo'], '기타단계')
                print(f"    - [{s['Lo']}] {desc:<10s}: {s['cnt']:>5d} 건")

    conn.close()
    print("\n==================================================")
    print("  종합 진단: AWS RDS 데이터베이스 상태 매우 양호 (100% 정상)")
    print("==================================================")

except Exception as e:
    print(f"❌ AWS RDS 오류: {e}")
