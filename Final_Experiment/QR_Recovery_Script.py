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

# 등급별 이미지 매핑 (Step3 로직 반영)
fruit_images_by_grade = {
    "Apples": ["apple2.png", "apple3.png", "apple4.png"],
    "Pears": ["pear2.png", "pear3.png", "pear4.png"],
    "Peaches": ["peach2.png", "peach3.png", "peach2.png"], # 복원 가능한 파일 위주
    "Tangerines": ["tangerine2.png", "tangerine3.png", "tangerine4.png"],
    "Melons": ["koreanmelon2.png", "koreanmelon3.png", "koreanmelon4.png"]
}

# 기본 로고 매핑 (등급 모를 때)
fruit_images_default = {
    "Apples": "apple.png", "Pears": "pear.png", "Peaches": "peach.png",
    "Tangerines": "tangerine.png", "Melons": "koreanmelon.png"
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

    # 등급 정보 처리 (A12~A15 단계 고려)
    # DB에 직접적인 'grade' 컬럼이 있거나, 수동으로 '상'을 할당해야 할 수 있음
    grade = row_dict.get("grade") or row_dict.get("Grade")
    if not grade and row_dict.get("Lo") in ["A12", "A13", "A14", "A15"]:
        grade = "상" # 출하 단계이므로 기본값을 '상'으로 설정 (필요시 수정 가능)
    
    if grade:
        params["grade"] = grade

    query_string = urlencode(params)
    qr_url = f"https://step5rundashboardpy-eu2ci93skt85rq8dgn5zxm.streamlit.app/?{query_string}"

    # QR 코드 생성 (Premium Style)
    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    # QR 색상 적용 (검정 대신 약간의 남색 계열로 프리미엄 느낌 추가 가능)
    qr_img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())

    # 로고 결정 및 삽입
    fruit_type = row_dict.get("FrT")
    logo_filename = None
    
    if fruit_type in fruit_images_by_grade:
        # 등급에 따른 이미지 선택
        if grade == "상": logo_filename = fruit_images_by_grade[fruit_type][0]
        elif grade == "중": logo_filename = fruit_images_by_grade[fruit_type][1]
        elif grade == "하": logo_filename = fruit_images_by_grade[fruit_type][2]
        else: logo_filename = fruit_images_default.get(fruit_type)
    else:
        logo_filename = fruit_images_default.get(fruit_type)

    if logo_filename:
        logo_path = os.path.join(LOGO_DIR, logo_filename)
        if not os.path.exists(logo_path):
            # 파일이 없으면 기본 파일로 대체
            logo_path = os.path.join(LOGO_DIR, fruit_images_default.get(fruit_type, ""))

        if os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path).convert("RGBA")
                # 로고를 컬러로 선명하게 리사이즈
                logo = logo.resize((200, 200), Image.LANCZOS)
                qr_img = qr_img.convert("RGBA")
                pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
                qr_img.paste(logo, pos, mask=logo)
            except Exception as e:
                print(f"⚠️ 로고 삽입 실패: {e}")

    # 파일명 생성
    lo = row_dict.get("Lo", "UNK")
    ac = row_dict.get("AC", "")
    fmid = row_dict.get("FmID", "")
    hd = row_dict.get("HD", "")
    hd_str = hd.strftime('%y%m%d') if isinstance(hd, datetime) else str(hd).replace("-", "")[2:8] if hd else "000000"

    filename = f"{lo}_{ac}{fmid}{hd_str}_{grade or 'N'}_QR.png"
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
            # id 컬럼이 없을 수 있으므로 정렬 없이 조회합니다.
            cursor.execute("SELECT * FROM qr")
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
