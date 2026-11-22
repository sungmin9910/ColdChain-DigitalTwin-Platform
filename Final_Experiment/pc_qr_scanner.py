import os
import sys
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote_plus
import pymysql

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from cloud_backend.supply_chain_spec import is_v3_lot_id

# ANSI 색상 코드 정의
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"

# AWS RDS 데이터베이스 연결 정보
DB_HOST = os.getenv("DB_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
DB_USER = "admin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_NAME = "lab225"
DB_PORT = 3306

MODES = {
    "AUTO": "🤖 AUTO (지능형 자동 판단 — 무색: A01→A02→B10→B12 / 유색: B12→B13→C10→C11→D10)",
    "A01": "A01 - 농가 창고 보관 (선택 · 무색 QR)",
    "A02": "A02 - 농가 출하 (1구간 출발 · 무색 QR)",
    "B10": "B10 - APC 입고 (1구간 도착 · 무색 QR)",
    "B12": "B12 - APC 창고 (선별 전 무색 QR / 선별 후 유색 QR)",
    "B13": "B13 - APC 출하 (2구간 출발 · 유색 QR · 창고 생략 직행 가능)",
    "C10": "C10 - 유통 창고 저장 (2구간 도착 · 유색 QR)",
    "C11": "C11 - 유통 출하 / 판매처 출발 (3구간 출발 · 유색 QR)",
    "D10": "D10 - 판매처 도착 (3구간 도착 · 유색 QR)",
}

MODE_KEYS = {
    "a": "AUTO",
    "A": "AUTO",
    "1": "A01",
    "2": "A02",
    "3": "B10",
    "4": "B12",
    "5": "B13",
    "6": "C10",
    "7": "C11",
    "8": "D10",
}

current_mode = "AUTO"


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    clear_console()
    print("=" * 72)
    print(f" {COLOR_CYAN}🚚 콜드체인 PC QR 스캐너 v3 (16자리 LotID / A00~D10 분기 지원) {COLOR_RESET}")
    print("=" * 72)
    print(f" DB Host     : {COLOR_BLUE}{DB_HOST}:{DB_PORT} ({DB_NAME}){COLOR_RESET}")
    print(f" 현재 단계   : {COLOR_YELLOW}★ {MODES[current_mode]} ★{COLOR_RESET}")
    print("-" * 72)
    print(" [조작 가이드]")
    print("  - 키 입력 + Enter: 스캔 단계 전환")
    print("    (A: AUTO | 1: A01 농가창고 | 2: A02 농가출하 | 3: B10 APC입고)")
    print("    (4: B12 APC창고 | 5: B13 APC출하 | 6: C10 유통창고 | 7: C11 유통출하 | 8: D10 판매처)")
    print("  - QR URL 또는 'MODE:A02' 특수 QR을 스캔/입력하세요. 종료: Ctrl+C")
    print("=" * 72)
    print()


def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        charset="utf8mb4",
    )


def get_latest_sensor_data():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                  COALESCE((SELECT lat FROM lab225.sensor_data WHERE device=B.device AND lat!=0 AND lng!=0 ORDER BY id DESC LIMIT 1),
                           (SELECT lat FROM lab225.sensor_data WHERE lat!=0 AND lng!=0 ORDER BY id DESC LIMIT 1)),
                  COALESCE((SELECT lng FROM lab225.sensor_data WHERE device=B.device AND lat!=0 AND lng!=0 ORDER BY id DESC LIMIT 1),
                           (SELECT lng FROM lab225.sensor_data WHERE lat!=0 AND lng!=0 ORDER BY id DESC LIMIT 1)),
                  B.temperature, B.humidity, B.device
                FROM (SELECT temperature, humidity, device FROM lab225.sensor_data ORDER BY id DESC LIMIT 1) B
            """)
            row = cursor.fetchone()
            if row:
                lat = f"{row[0]}" if row[0] is not None else "NULL"
                lon = f"{row[1]}" if row[1] is not None else "NULL"
                tp = f"'{row[2]}'" if row[2] is not None else "NULL"
                hm = f"'{row[3]}'" if row[3] is not None else "NULL"
                dev = f"'{row[4]}'" if row[4] is not None else "NULL"
                return lat, lon, tp, hm, dev
    except Exception as e:
        print(f"{COLOR_RED}[-] 센서 데이터 조회 에러: {e}{COLOR_RESET}")
    finally:
        if conn:
            conn.close()
    return "NULL", "NULL", "NULL", "NULL", "NULL"


def get_raw_param(url, param):
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        val = query_params.get(param, [None])[0]
        if val is None or val == "":
            return ""
        return unquote_plus(val).replace("'", "").strip()
    except Exception:
        return ""


def to_sql(v):
    return f"'{v}'" if v else "NULL"


def extract_lot_id(url):
    for k in ("LotID", "lot_id", "FmID", "fmid"):
        v = get_raw_param(url, k)
        if v:
            return v
    try:
        parsed_url = urlparse(url)
        if "/qr/" in parsed_url.path:
            legacy_id = parsed_url.path.split("/qr/")[-1].split("/")[0]
            if legacy_id:
                return legacy_id
    except Exception:
        pass
    return ""


def extract_grade_code(url):
    raw_g = get_raw_param(url, "pkg_grade") or get_raw_param(url, "grade")
    if not raw_g:
        return ""
    g_up = raw_g.upper()
    if g_up in ("B", "M", "MEDIUM") or "중" in raw_g:
        return "B"
    if g_up in ("C", "L", "LOW") or "하" in raw_g:
        return "C"
    if g_up in ("A", "H", "HIGH") or "상" in raw_g:
        return "A"
    return ""


def process_scan(scanned_data):
    global current_mode
    scanned_data = scanned_data.strip()
    if not scanned_data:
        return

    if scanned_data.startswith("MODE:"):
        new_mode = scanned_data.replace("MODE:", "").strip().upper()
        if new_mode in MODES:
            current_mode = new_mode
            print_header()
            print(f"{COLOR_GREEN}[+] QR 스캔으로 모드 변경 -> {MODES[current_mode]}{COLOR_RESET}\n")
        else:
            print(f"{COLOR_RED}[-] 잘못된 모드 지정 QR: {new_mode}{COLOR_RESET}\n")
        return

    clean_lot = extract_lot_id(scanned_data)
    if not clean_lot:
        print(f"{COLOR_RED}[-] 스캔된 데이터에서 LotID/FmID를 찾을 수 없습니다: {scanned_data}{COLOR_RESET}\n")
        return

    clean_ac = get_raw_param(scanned_data, "AC")
    clean_fm = get_raw_param(scanned_data, "FmID")
    clean_cc = get_raw_param(scanned_data, "CC")
    if is_v3_lot_id(clean_lot):
        if not clean_ac:
            clean_ac = clean_lot[0:5]
        if not clean_fm:
            clean_fm = clean_lot[5:7]
        if not clean_cc:
            clean_cc = clean_lot[7:10]
    elif not clean_fm:
        clean_fm = clean_lot

    scanned_grade = extract_grade_code(scanned_data)
    display_id = f"{clean_lot}-{scanned_grade}" if scanned_grade else clean_lot

    print(f"\n[*] QR 스캔 감지 -> 대상 ID: {COLOR_YELLOW}{display_id}{COLOR_RESET} (QR 종류: {'유색 ' + scanned_grade if scanned_grade else '무색 원물'})")
    lat, lon, tp, hm, dev = get_latest_sensor_data()
    print(f"[+] 최신 FDT 센서 -> Device: {dev}, Temp: {tp}, Hum: {hm}, GPS: ({lat}, {lon})")

    sql_lot = to_sql(clean_lot)
    sql_fm = to_sql(clean_fm)
    sql_ac = to_sql(clean_ac)
    sql_cc = to_sql(clean_cc)
    frt = to_sql(get_raw_param(scanned_data, "FrT"))
    vt = to_sql(get_raw_param(scanned_data, "Vt"))
    ct = to_sql(get_raw_param(scanned_data, "Ct"))
    hd = to_sql(get_raw_param(scanned_data, "HD"))
    dd = to_sql(get_raw_param(scanned_data, "DD"))
    qt = to_sql(get_raw_param(scanned_data, "Qt"))
    mt = to_sql(get_raw_param(scanned_data, "Mt"))
    hn = to_sql(get_raw_param(scanned_data, "HN"))
    std = to_sql(get_raw_param(scanned_data, "StD"))

    lot_where = f"(Q.LotID = {sql_lot} OR (Q.LotID IS NULL AND Q.FmID = {sql_lot}))"
    lot_where_plain = f"(LotID = {sql_lot} OR (LotID IS NULL AND FmID = {sql_lot}))"

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SET time_zone = '+09:00'")

            target_mode = current_mode
            if current_mode == "AUTO":
                last_lo = "NONE"
                if scanned_grade:
                    cur.execute(
                        f"SELECT Lo FROM lab225.qr WHERE {lot_where_plain} "
                        f"AND Lo IN ('B12','B13','C10','C11','D10') AND pkg_grade = '{scanned_grade}' "
                        f"ORDER BY id DESC LIMIT 1"
                    )
                    r = cur.fetchone()
                    if r and r[0]:
                        last_lo = str(r[0]).strip().upper()
                    if last_lo == "NONE":
                        cur.execute(
                            f"SELECT Lo FROM lab225.qr WHERE {lot_where_plain} "
                            f"AND Lo IN ('B10','B11','B12') AND (pkg_grade IS NULL OR pkg_grade = '') "
                            f"ORDER BY id DESC LIMIT 1"
                        )
                        r2 = cur.fetchone()
                        if r2 and r2[0]:
                            last_lo = str(r2[0]).strip().upper()

                    if last_lo in ("NONE", "B11", "B10"):
                        target_mode = "B12"
                    elif last_lo == "B12":
                        target_mode = "B13"
                    elif last_lo == "B13":
                        target_mode = "C10"
                    elif last_lo == "C10":
                        target_mode = "C11"
                    elif last_lo == "C11":
                        target_mode = "D10"
                    elif last_lo == "D10":
                        print(f"{COLOR_YELLOW}[!] 이미 판매처 도착(D10) 완료된 상품입니다 ({display_id}).{COLOR_RESET}\n")
                        return
                else:
                    cur.execute(
                        f"SELECT Lo FROM lab225.qr WHERE {lot_where_plain} "
                        f"AND (pkg_grade IS NULL OR pkg_grade = '') ORDER BY id DESC LIMIT 1"
                    )
                    r = cur.fetchone()
                    if r and r[0]:
                        last_lo = str(r[0]).strip().upper()

                    if last_lo in ("NONE", "A00"):
                        target_mode = "A01"
                    elif last_lo == "A01":
                        target_mode = "A02"
                    elif last_lo == "A02":
                        target_mode = "B10"
                    elif last_lo == "B10":
                        target_mode = "B12"
                    elif last_lo == "B12":
                        print(f"{COLOR_YELLOW}[!] 선별 전 APC 창고(B12) 보관 중입니다. 포털에서 B11 선별 후 유색 QR을 스캔하세요.{COLOR_RESET}\n")
                        return
                    else:
                        print(f"{COLOR_YELLOW}[!] 이미 선별(B11) 이후 단계입니다. 유색 QR을 스캔하세요.{COLOR_RESET}\n")
                        return
                print(f"[*] 🎯 [AUTO 판단] 최근={last_lo} -> 다음 단계: {COLOR_GREEN}★ {target_mode} ★{COLOR_RESET}")

            cur.execute(f"SELECT id FROM lab225.qr WHERE {lot_where_plain} AND (pkg_grade IS NULL OR pkg_grade = '') ORDER BY id DESC LIMIT 1")
            base_exists = cur.fetchone() is not None

            eff_grade_sql = f"'{scanned_grade}'" if scanned_grade else "'A'"
            query = ""

            if target_mode == "A01":
                if base_exists:
                    query = (
                        f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Tp, Hm, Lat, lon, truck_device) "
                        f"SELECT 'A01', Q.AC, Q.FmID, {sql_lot}, COALESCE(Q.CropCode, {sql_cc}), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, NOW(), {tp}, {hm}, {lat}, {lon}, COALESCE({dev}, Q.truck_device) "
                        f"FROM lab225.qr Q WHERE {lot_where} AND Q.Lo = 'A00' ORDER BY Q.id DESC LIMIT 1"
                    )
                else:
                    query = (
                        f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Tp, Hm, Lat, lon, truck_device) "
                        f"VALUES ('A01', {sql_ac}, {sql_fm}, {sql_lot}, {sql_cc}, {frt}, {vt}, {ct}, {hd}, {dd}, {qt}, {mt}, {hn}, {std}, NOW(), {tp}, {hm}, {lat}, {lon}, {dev})"
                    )
            elif target_mode == "A02":
                if base_exists:
                    query = (
                        f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_DD, Tp, Hm, Lat, lon, truck_device) "
                        f"SELECT 'A02', Q.AC, Q.FmID, {sql_lot}, COALESCE(Q.CropCode, {sql_cc}), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, NOW(), Q.Tp, Q.Hm, {lat}, {lon}, COALESCE({dev}, Q.truck_device) "
                        f"FROM lab225.qr Q WHERE {lot_where} AND Q.Lo IN ('A01','A00') ORDER BY Q.id DESC LIMIT 1"
                    )
                else:
                    query = (
                        f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_DD, Lat, lon, truck_device) "
                        f"VALUES ('A02', {sql_ac}, {sql_fm}, {sql_lot}, {sql_cc}, {frt}, {vt}, {ct}, {hd}, {dd}, {qt}, {mt}, {hn}, {std}, NOW(), {lat}, {lon}, {dev})"
                    )
            elif target_mode == "B10":
                if base_exists:
                    query = (
                        f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_DD, APC_AD, Lat, lon, truck_device) "
                        f"SELECT 'B10', Q.AC, Q.FmID, {sql_lot}, COALESCE(Q.CropCode, {sql_cc}), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_DD, NOW(), {lat}, {lon}, COALESCE(Q.truck_device, {dev}) "
                        f"FROM lab225.qr Q WHERE {lot_where} AND Q.Lo IN ('A02','A01','A00') ORDER BY Q.id DESC LIMIT 1"
                    )
                else:
                    query = (
                        f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, APC_AD, Lat, lon, truck_device) "
                        f"VALUES ('B10', {sql_ac}, {sql_fm}, {sql_lot}, {sql_cc}, {frt}, {vt}, {ct}, {hd}, {dd}, {qt}, {mt}, {hn}, {std}, NOW(), {lat}, {lon}, {dev})"
                    )
            elif target_mode == "B12":
                if not scanned_grade:
                    query = (
                        f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_DD, APC_AD, APC_StD, Tp, Hm, Lat, lon, truck_device, pkg_grade) "
                        f"SELECT 'B12', Q.AC, Q.FmID, {sql_lot}, COALESCE(Q.CropCode, {sql_cc}), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_DD, Q.APC_AD, NOW(), {tp}, {hm}, {lat}, {lon}, COALESCE({dev}, Q.truck_device), NULL "
                        f"FROM lab225.qr Q WHERE {lot_where} AND Q.Lo = 'B10' ORDER BY Q.id DESC LIMIT 1"
                    )
                else:
                    query = (
                        f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_DD, APC_AD, APC_RT, APC_StD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) "
                        f"SELECT 'B12', Q.AC, Q.FmID, {sql_lot}, COALESCE(Q.CropCode, {sql_cc}), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_DD, Q.APC_AD, Q.APC_RT, NOW(), {tp}, {hm}, {lat}, {lon}, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE({dev}, Q.truck_device), {eff_grade_sql} "
                        f"FROM lab225.qr Q WHERE {lot_where} AND Q.Lo = 'B11' ORDER BY Q.id DESC LIMIT 1"
                    )
            elif target_mode == "B13":
                query = (
                    f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_DD, APC_AD, APC_RT, APC_StD, APC_OP, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) "
                    f"SELECT 'B13', Q.AC, Q.FmID, {sql_lot}, COALESCE(Q.CropCode, {sql_cc}), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_StD, NOW(), Q.Tp, Q.Hm, {lat}, {lon}, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE({dev}, Q.truck_device), {eff_grade_sql} "
                    f"FROM lab225.qr Q WHERE {lot_where} AND ((Q.Lo = 'B12' AND Q.pkg_grade = {eff_grade_sql}) OR Q.Lo = 'B11') "
                    f"ORDER BY CASE WHEN Q.Lo = 'B12' AND Q.pkg_grade = {eff_grade_sql} THEN 0 ELSE 1 END, Q.id DESC LIMIT 1"
                )
            elif target_mode == "C10":
                query = (
                    f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_DD, APC_AD, APC_RT, APC_StD, APC_OP, Dist_StD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) "
                    f"SELECT 'C10', Q.AC, Q.FmID, {sql_lot}, COALESCE(Q.CropCode, {sql_cc}), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_StD, Q.APC_OP, NOW(), {tp}, {hm}, {lat}, {lon}, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE(Q.truck_device, {dev}), {eff_grade_sql} "
                    f"FROM lab225.qr Q WHERE {lot_where} AND Q.Lo = 'B13' AND COALESCE(Q.pkg_grade, 'A') = {eff_grade_sql} ORDER BY Q.id DESC LIMIT 1"
                )
            elif target_mode == "C11":
                query = (
                    f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_DD, APC_AD, APC_RT, APC_StD, APC_OP, Dist_StD, Dist_OP, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) "
                    f"SELECT 'C11', Q.AC, Q.FmID, {sql_lot}, COALESCE(Q.CropCode, {sql_cc}), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_StD, Q.APC_OP, Q.Dist_StD, NOW(), Q.Tp, Q.Hm, {lat}, {lon}, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE({dev}, Q.truck_device), {eff_grade_sql} "
                    f"FROM lab225.qr Q WHERE {lot_where} AND Q.Lo IN ('C10','B13') AND COALESCE(Q.pkg_grade, 'A') = {eff_grade_sql} ORDER BY Q.id DESC LIMIT 1"
                )
            elif target_mode == "D10":
                query = (
                    f"INSERT INTO lab225.qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Farm_StD, Farm_DD, APC_AD, APC_RT, APC_StD, APC_OP, Dist_StD, Dist_OP, Retail_AD, Tp, Hm, Lat, lon, AGrade, BGrade, CGrade, DefectRate, truck_device, pkg_grade) "
                    f"SELECT 'D10', Q.AC, Q.FmID, {sql_lot}, COALESCE(Q.CropCode, {sql_cc}), Q.FrT, Q.Vt, Q.Ct, Q.HD, Q.DD, Q.Qt, Q.Mt, Q.HN, Q.Std, Q.Farm_StD, Q.Farm_DD, Q.APC_AD, Q.APC_RT, Q.APC_StD, Q.APC_OP, Q.Dist_StD, Q.Dist_OP, NOW(), Q.Tp, Q.Hm, {lat}, {lon}, Q.AGrade, Q.BGrade, Q.CGrade, Q.DefectRate, COALESCE(Q.truck_device, {dev}), {eff_grade_sql} "
                    f"FROM lab225.qr Q WHERE {lot_where} AND Q.Lo IN ('C11','C10','B13') AND COALESCE(Q.pkg_grade, 'A') = {eff_grade_sql} ORDER BY Q.id DESC LIMIT 1"
                )

            affected = cur.execute(query)
            conn.commit()
            if affected > 0:
                print(f"{COLOR_GREEN}[+] DB 저장 성공! [대상: {display_id} | 단계: {target_mode}]{COLOR_RESET}\n")
            else:
                print(f"{COLOR_RED}[-] DB 저장 실패: 선행 단계 이력이 존재하지 않습니다.{COLOR_RESET}\n")
    except Exception as e:
        print(f"{COLOR_RED}[-] DB 처리 오류: {e}{COLOR_RESET}\n")
    finally:
        if conn:
            conn.close()


def main():
    global current_mode
    print_header()
    try:
        conn = get_db_connection()
        conn.close()
        print(f"{COLOR_GREEN}[+] AWS RDS 연결 성공! ({DB_HOST}){COLOR_RESET}\n")
        time.sleep(1.0)
        print_header()
    except Exception as e:
        print(f"{COLOR_RED}[-] DB 연결 실패: {e}{COLOR_RESET}")

    while True:
        try:
            prompt = f"{COLOR_BLUE}[{current_mode}]{COLOR_RESET} 스캔 대기 중 (또는 A, 1~8 입력): "
            user_input = input(prompt).strip()
            if not user_input:
                continue
            if user_input in MODE_KEYS:
                current_mode = MODE_KEYS[user_input]
                print_header()
                print(f"{COLOR_GREEN}[+] 모드 변경 -> {MODES[current_mode]}{COLOR_RESET}\n")
            else:
                process_scan(user_input)
        except KeyboardInterrupt:
            print(f"\n{COLOR_YELLOW}[!] 프로그램을 종료합니다.{COLOR_RESET}")
            break
        except Exception as e:
            print(f"{COLOR_RED}[-] 오류: {e}{COLOR_RESET}\n")


if __name__ == "__main__":
    if os.name == "nt":
        os.system("")
    main()
