import os
import sys
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import pymysql

# ANSI 색상 코드 정의
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"

# AWS RDS 데이터베이스 연결 정보
DB_HOST = "15.165.68.30"
DB_USER = "admin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_NAME = "lab225"
DB_PORT = 3306

MODES = {
    "A10": "A10 - 박스 입고 (APC 입고)",
    "A11": "A11 - 세척 완료 (APC 세척)",
    "A12": "A12 - 수송 시작 (APC 출하/수송)",
    "A13": "A13 - 포장 완료 (유통 센터 포장)",
    "A14": "A14 - 저장 완료 (저장소 입고)",
    "A15": "A15 - 최종 출하 (소비지 출하)"
}

MODE_KEYS = {
    "0": "A10",
    "1": "A11",
    "2": "A12",
    "3": "A13",
    "4": "A14",
    "5": "A15"
}

current_mode = "A10"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_console()
    print("=" * 60)
    print(f" {COLOR_CYAN}🚚 콜드체인 PC QR 스캐너 (ESP32 에뮬레이터) {COLOR_RESET}")
    print("=" * 60)
    print(f" DB Host     : {COLOR_BLUE}{DB_HOST}:{DB_PORT}{COLOR_RESET}")
    print(f" DB User     : {DB_USER}")
    print(f" DB Name     : {DB_NAME}")
    print(f" 현재 단계   : {COLOR_YELLOW}★ {MODES[current_mode]} ★{COLOR_RESET}")
    print("-" * 60)
    print(" [조작 가이드]")
    print("  - 숫자 키 입력 후 Enter: 스캔 단계 변경")
    print("    (0: A10, 1: A11, 2: A12, 3: A13, 4: A14, 5: A15)")
    print("  - QR 코드 스캔(또는 붙여넣기 + Enter) 시 데이터가 DB에 저장됩니다.")
    print("  - 'MODE:A11' 형태의 특수 QR을 스캔해도 단계가 변경됩니다.")
    print("  - 종료하려면 Ctrl+C를 누르세요.")
    print("=" * 60)
    print()

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        charset="utf8mb4"
    )

def get_latest_sensor_data():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 가장 최근 센서 데이터 1건 조회
            cursor.execute("SELECT lat, lng, temperature, humidity FROM lab225.sensor_data ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                lat = f"'{row[0]}'" if row[0] is not None else "NULL"
                lon = f"'{row[1]}'" if row[1] is not None else "NULL"
                tp = f"'{row[2]}'" if row[2] is not None else "NULL"
                hm = f"'{row[3]}'" if row[3] is not None else "NULL"
                return lat, lon, tp, hm
    except Exception as e:
        print(f"{COLOR_RED}[-] 센서 데이터(GPS/온습도) 조회 중 에러 발생: {e}{COLOR_RESET}")
    finally:
        if conn:
            conn.close()
    return "NULL", "NULL", "NULL", "NULL"

def get_query_param(url, param):
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        val = query_params.get(param, [None])[0]
        if val is None or val == "":
            return "NULL"
        return f"'{val}'"
    except Exception:
        return "NULL"

def get_fmid(url):
    # 1. 새로운 Streamlit 쿼리 파라미터 방식 (?FmID=33)
    fmid = get_query_param(url, "FmID")
    if fmid != "NULL" and fmid != "''":
        return fmid
    
    # 2. 기존 URL 방식 (/qr/33?)
    try:
        parsed_url = urlparse(url)
        path = parsed_url.path
        if "/qr/" in path:
            legacy_id = path.split("/qr/")[-1].split('/')[0]
            if legacy_id:
                return f"'{legacy_id}'"
    except Exception:
        pass
    return "NULL"

def process_scan(scanned_data):
    global current_mode
    
    scanned_data = scanned_data.strip()
    if not scanned_data:
        return

    # 1. 단계 변경 QR 검증
    if scanned_data.startswith("MODE:"):
        new_mode = scanned_data.replace("MODE:", "").strip().upper()
        if new_mode in MODES:
            current_mode = new_mode
            print_header()
            print(f"{COLOR_GREEN}[+] QR 스캔을 통해 모드가 {MODES[current_mode]}(으)로 변경되었습니다.{COLOR_RESET}\n")
        else:
            print(f"{COLOR_RED}[-] 잘못된 모드 지정 QR 코드입니다: {new_mode}{COLOR_RESET}\n")
        return

    # 2. 일반 과일 QR 파싱
    fmid = get_fmid(scanned_data)
    if fmid == "NULL" or fmid == "''":
        print(f"{COLOR_RED}[-][경고] 스캔된 데이터에서 농가 ID(FmID)를 찾을 수 없습니다.{COLOR_RESET}")
        print(f"스캔된 원본: {scanned_data}\n")
        return

    print(f"\n[*] QR 코드 스캔 감지: {COLOR_GREEN}{scanned_data}{COLOR_RESET}")
    print(f"[*] 추출된 농가 ID (FmID): {COLOR_YELLOW}{fmid}{COLOR_RESET}")

    ac = get_query_param(scanned_data, "AC")
    frt = get_query_param(scanned_data, "FrT")
    vt = get_query_param(scanned_data, "Vt")
    ct = get_query_param(scanned_data, "Ct")
    hd = get_query_param(scanned_data, "HD")
    dd = get_query_param(scanned_data, "DD")
    qt = get_query_param(scanned_data, "Qt")
    mt = get_query_param(scanned_data, "Mt")
    hn = get_query_param(scanned_data, "HN")
    std = get_query_param(scanned_data, "StD")
    rp = get_query_param(scanned_data, "Rp")

    # DB에서 최신 GPS/온습도 데이터 가져오기
    print("[*] 데이터베이스에서 최신 센서 데이터(GPS, 온습도) 수신 중...")
    lat, lon, tp, hm = get_latest_sensor_data()
    print(f"[+] 최근 센서 데이터 -> Lat: {lat}, Lng: {lon}, Temp: {tp}, Hum: {hm}")

    # 현재 모드에 맞게 쿼리 생성
    query = ""
    if current_mode == "A10":
        query = f"""
        INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, Lat, lon)
        VALUES ('A10', {ac}, {fmid}, {frt}, {vt}, {ct}, {hd}, {dd}, {qt}, {mt}, {hn}, {std}, {rp}, NOW(), {lat}, {lon})
        """
    elif current_mode == "A11":
        query = f"""
        INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, Lat, lon)
        SELECT 'A11', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, NOW(), {lat}, {lon}
        FROM lab225.qr WHERE FmID = {fmid} AND APC_AD IS NOT NULL ORDER BY APC_AD DESC LIMIT 1
        """
    elif current_mode == "A12":
        query = f"""
        INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, Lat, lon)
        SELECT 'A12', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, NOW(), {lat}, {lon}
        FROM lab225.qr WHERE Lo = 'A11' AND FmID = {fmid} ORDER BY APC_WD DESC LIMIT 1
        """
    elif current_mode == "A13":
        query = f"""
        INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, Lat, lon, AGrade, BGrade, CGrade, DefectRate)
        SELECT 'A13', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, NOW(), {lat}, {lon}, AGrade, BGrade, CGrade, DefectRate
        FROM lab225.qr WHERE Lo = 'A12' AND FmID = {fmid} ORDER BY APC_RT DESC LIMIT 1
        """
    elif current_mode == "A14":
        query = f"""
        INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate)
        SELECT 'A14', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, NOW(), {tp}, {hm}, {lat}, {lon}, AGrade, BGrade, CGrade, DefectRate
        FROM lab225.qr WHERE Lo = 'A13' AND FmID = {fmid} ORDER BY APC_PT DESC LIMIT 1
        """
    elif current_mode == "A15":
        query = f"""
        INSERT INTO lab225.qr (Lo, AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, APC_OP, Lat, lon, AGrade, BGrade, CGrade, DefectRate)
        SELECT 'A15', AC, FmID, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, StD, Rp, APC_AD, APC_WD, APC_RT, APC_PT, APC_StD, NOW(), {lat}, {lon}, AGrade, BGrade, CGrade, DefectRate
        FROM lab225.qr WHERE Lo = 'A14' AND FmID = {fmid} ORDER BY APC_StD DESC LIMIT 1
        """

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # SQL 시간대를 한국(KST)으로 맞춤
            cursor.execute("SET time_zone = '+09:00'")
            affected = cursor.execute(query)
            conn.commit()
            
            if affected > 0:
                print(f"{COLOR_GREEN}[+] DB 저장 완료! [단계: {current_mode}]{COLOR_RESET}\n")
            else:
                print(f"{COLOR_RED}[-] DB 저장 실패: 조건에 맞는 이전 단계 이력 데이터가 존재하지 않습니다.{COLOR_RESET}\n")
    except Exception as e:
        print(f"{COLOR_RED}[-] DB 저장 중 쿼리 오류 발생: {e}{COLOR_RESET}\n")
    finally:
        if conn:
            conn.close()

def main():
    global current_mode
    print_header()
    
    # DB 연결 테스트 진행
    print("[*] AWS DB 연결 테스트 중...")
    try:
        conn = get_db_connection()
        conn.close()
        print(f"{COLOR_GREEN}[+] DB 연결 성공! (AWS RDS: {DB_HOST}){COLOR_RESET}\n")
        time.sleep(1.5)
        print_header()
    except Exception as e:
        print(f"{COLOR_RED}[-] DB 연결 실패! 설정된 패스워드나 퍼블릭 액세스 설정을 확인하세요.{COLOR_RESET}")
        print(f"    오류 내용: {e}")
        input("엔터를 누르면 계속 진행하지만, DB 저장은 되지 않을 수 있습니다...")
        print_header()

    while True:
        try:
            # 대기
            prompt = f"{COLOR_BLUE}[{current_mode}]{COLOR_RESET} 스캔 대기 중 (또는 모드 번호 입력): "
            user_input = input(prompt).strip()
            
            if not user_input:
                continue
                
            # 모드 변경 명령인지 확인 (0 ~ 5)
            if user_input in MODE_KEYS:
                current_mode = MODE_KEYS[user_input]
                print_header()
                print(f"{COLOR_GREEN}[+] 스캔 단계가 {MODES[current_mode]}(으)로 수동 전환되었습니다.{COLOR_RESET}\n")
            else:
                # QR 스캔 처리
                process_scan(user_input)
                
        except KeyboardInterrupt:
            print(f"\n{COLOR_YELLOW}[!] 프로그램을 종료합니다.{COLOR_RESET}")
            break
        except Exception as e:
            print(f"{COLOR_RED}[-] 오류 발생: {e}{COLOR_RESET}\n")

if __name__ == "__main__":
    # ANSI 이스케이프 코드 활성화 (Windows CMD 대응)
    if os.name == 'nt':
        os.system('')
    main()
