import pymysql
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image
import os
import json
from urllib.parse import urlencode
from dotenv import load_dotenv
from datetime import datetime

# .env 파일 로드
load_dotenv()

# --- 설정 정보 ---
DB_HOST = "15.165.68.30"
DB_USER = "admin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_NAME = "lab225"
DB_PORT = 3306

# 로고 파일 및 출력 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(BASE_DIR, "1_PC_QR_Generators")
OUTPUT_DIR = os.path.join(BASE_DIR, "recovered_qrs")

fruit_images = {
    "Apples": "apple.png", 
    "Pears": "pear.png", 
    "Peaches": "peach.png",
    "Tangerines": "tangerine.png", 
    "Melons": "koreanmelon.png"
}

# 파라미터 매핑 규칙
key_map = {
    "AC": "AC", "FmID": "FmID", "Ct": "Ct", "FrT": "FrT",
    "Vt": "Vt", "HD": "HD", "DD": "DD", "StD": "StD",
    "Mt": "Mt", "HN": "HN", "Qt": "Qt", "Rp": "Rp"
}

def get_db_connection():
    try:
        return pymysql.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_NAME, port=DB_PORT, charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        return None

def generate_qr_from_row(row_dict):
    """DB 한 행의 데이터를 바탕으로 QR 생성"""
    params = {}
    for db_key, qr_key in key_map.items():
        val = row_dict.get(db_key)
        if val is not None:
            if isinstance(val, datetime):
                val = val.strftime('%Y-%m-%d')
            params[qr_key] = val

    query_string = urlencode(params)
    qr_url = f"https://step5rundashboardpy-eu2ci93skt85rq8dgn5zxm.streamlit.app/?{query_string}"

    # QR 코드 생성
    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())

    # 로고 삽입
    fruit_type = row_dict.get("FrT")
    logo_filename = fruit_images.get(fruit_type)
    if logo_filename:
        logo_path = os.path.join(LOGO_DIR, logo_filename)
        if os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path).convert("RGBA")
                logo = logo.resize((200, 200), Image.LANCZOS)
                qr_img = qr_img.convert("RGBA")
                pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
                qr_img.paste(logo, pos, mask=logo)
            except Exception as e:
                pass # 로고 실패 시 그냥 생성

    # 파일명 생성
    lo = row_dict.get("Lo", "UNK")
    ac = row_dict.get("AC", "")
    fmid = row_dict.get("FmID", "")
    hd = row_dict.get("HD", "")
    hd_str = hd.strftime('%y%m%d') if isinstance(hd, datetime) else str(hd).replace("-", "")[2:8] if hd else "000000"

    filename = f"{lo}_{ac}{fmid}{hd_str}_QR.png"
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    qr_img.save(file_path)
    return filename

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 출력 폴더 생성됨: {OUTPUT_DIR}")

    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM qr ORDER BY id DESC")
            rows = cursor.fetchall()
            
            print(f"📊 총 {len(rows)}개의 레코드를 발견했습니다. 복원을 시작합니다...")
            
            count = 0
            for row in rows:
                try:
                    generate_qr_from_row(row)
                    count += 1
                    if count % 10 == 0:
                        print(f"⏳ 진행 중... ({count}/{len(rows)})")
                except Exception as e:
                    print(f"❌ 데이터 처리 중 오류 (ID: {row.get('id')}): {e}")

            print(f"\n✅ 복원 완료! 총 {count}개의 QR 코드가 생성되었습니다.")
            print(f"📍 저장 위치: {OUTPUT_DIR}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()
