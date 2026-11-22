#라이브러리가 많다 해결책이 필요하다.
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
from tkcalendar import DateEntry
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from PIL import Image, ImageTk
import datetime
import mysql.connector
from urllib.parse import urlencode
import re
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from cloud_backend.supply_chain_spec import (
    get_crop_code,
    normalize_area_code,
    normalize_fmid_2digit,
    build_lot_id_16,
)

# --- [추가] 무결성 검증을 위한 라이브러리 ---
import hashlib
import json

# --- [추가] 보안을 위한 dotenv 환경 변수 로드 ---
import os
from dotenv import load_dotenv
load_dotenv() # .env 파일에서 비밀번호를 안전하게 불러옵니다.

# --- DB 연결 정보 (AWS RDS) ---
DB_HOST = "15.165.68.30"
DB_USER = "admin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345678")
DB_NAME = "lab225"
DB_PORT = 3306

# --- [추가] 블록체인 시뮬레이션 파일 ---
BLOCKCHAIN_FILE = "blockchain_ledger.json"

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, charset="utf8mb4",
        collation="utf8mb4_general_ci", port=DB_PORT
    )

# 변수들
zip_codes = ["55630", "55631", "55632", "55633", "55634", "55635"]
fruit_types = ["Apples", "Pears", "Peaches", "Tangerines", "Melons"]
farming_methods = ["Organic", "Conventional"]

fruit_images = {
    "Apples": "apple.png", "Pears": "pear.png", "Peaches": "peach.png",
    "Tangerines": "tangerine.png", "Melons": "koreanmelon.png"
}

font_size = 15
uniform_combobox_width = 25

# --- [추가] 해시 생성 및 블록체인 저장 함수 ---
def calculate_hash(data_dict):
    """데이터 딕셔너리를 SHA-256 해시값으로 변환"""
    # 딕셔너리 정렬 후 문자열 변환 (순서가 바뀌면 해시가 달라지므로 정렬 필수)
    data_str = json.dumps(data_dict, sort_keys=True, default=str).encode()
    return hashlib.sha256(data_str).hexdigest()

def save_to_blockchain(data_hash, metadata):
    """해시값을 로컬 JSON 파일에 저장 (블록체인 기록 시뮬레이션)"""
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hash": data_hash,
        "metadata": metadata  # 어떤 데이터의 해시인지 식별용
    }
    
    chain_data = []
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE, "r", encoding="utf-8") as f:
                chain_data = json.load(f)
        except:
            chain_data = []
    
    chain_data.append(entry)
    
    with open(BLOCKCHAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(chain_data, f, indent=4, ensure_ascii=False)
    
    print(f"🔒 [Blockchain] Block Recorded: {data_hash}")

# --- 기존 헬퍼 함수들 ---
def format_phone_number(entry):
    current_text = entry.get()
    formatted_text = re.sub(r'\D', '', current_text)
    entry.delete(0, tk.END)
    entry.insert(0, formatted_text)

def get_selected_harvest_date(): return harvest_date_picker.get_date()
def get_selected_deliver_date(): return deliver_date_picker.get_date()
def get_selected_storage_date(): return storage_date_picker.get_date()

def generate_filename(area_code, farmer_id, harvest_date, fruit_type="Apples", variety=""):
    return build_lot_id_16(area_code, farmer_id, fruit_type, variety, harvest_date)

# QR 코드 생성 함수 (v3 16자리 LotID + aT 3자리 작물코드 지원)
def generate_qr_code(data, filename):
    key_map = {
        "Lot ID": "LotID", "Area Code": "AC", "Farmer ID": "FmID", "Crop Code": "CC",
        "Contact Info": "Ct", "Fruit Type": "FrT", "Variety": "Vt", "Harvest Date": "HD",
        "Deliver Date": "DD", "Storage Date": "StD", "Farming Method": "Mt",
        "Harvesting Number": "HN", "Quantity": "Qt", "Ag Practice": "Rp"
    }
    params = {}
    for key, value in data.items():
        mapped_key = key_map.get(key)
        if mapped_key and value not in (None, ""):
            params[mapped_key] = value

    query_string = urlencode(params)
    qr_url = f"https://coldchain-digitaltwin-platform-xg7e8qvdp9lkcupwdcmceh.streamlit.app/?{query_string}"

    print(f"[INFO] QR URL: {qr_url}")

    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(image_factory=StyledPilImage, module_drawer=RoundedModuleDrawer())

    fruit_type = data.get("Fruit Type")
    fruit_filename = fruit_images.get(fruit_type)
    
    # 이미지 경로 처리 개선
    if fruit_filename:
        if os.path.exists(fruit_filename):
            fruit_image_path = fruit_filename
        else:
            fruit_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), fruit_filename)
    else:
        fruit_image_path = None

    if fruit_image_path and os.path.exists(fruit_image_path):
        try:
            logo = Image.open(fruit_image_path).convert("RGBA")
            logo = logo.resize((200, 200), Image.LANCZOS)
            qr_img = qr_img.convert("RGBA")
            pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
            qr_img.paste(logo, pos, mask=logo)
        except Exception as e:
            print(f"[ERROR] Logo insertion failed: {e}")

    file_path = f"{filename}_QR.png"
    qr_img.save(file_path)

    qr_img_resized = qr_img.resize((150, 150), Image.LANCZOS)
    qr_image = ImageTk.PhotoImage(qr_img_resized)
    qr_label.config(image=qr_image)
    qr_label.image = qr_image

# --- [핵심 수정] 저장 함수 ---
current_data_cache = {} # 검증 실험을 위해 마지막 저장 데이터를 임시 보관

def save_all_formats():
    global current_data_cache  # 검증을 위해 데이터를 잠시 기억하는 변수 사용
    
    # 1. GUI 입력창에서 값 가져오기
    area_code = area_code_combobox.get()
    farmer_id = farmer_id_entry.get()
    fruit_type = fruit_type_combobox.get()
    variety = variety_combobox.get()
    contact_info = contact_info_entry.get()
    harvest_date = get_selected_harvest_date()
    deliver_date = get_selected_deliver_date()
    storage_date = get_selected_storage_date()
    farming_method = farming_method_combobox.get()
    harvesting_number = harvesting_number_entry.get()
    quantity = quantity_entry.get()
    ag_practice = ag_practice_entry.get()

    # 2. 필수 입력값 확인
    if not all([area_code, farmer_id, fruit_type, variety, contact_info]):
        status_label_main_section.config(text="Please fill all required fields!", foreground="red")
        return

    # 3. 16자리 LotID 및 aT 3자리 작물코드 생성 (AreaCode5 + FmID2 + CropCode3 + YYMMDD6)
    ac5 = normalize_area_code(area_code)
    fm2 = normalize_fmid_2digit(farmer_id)
    cc3 = get_crop_code(fruit_type, variety)
    lot_id_16 = build_lot_id_16(ac5, fm2, fruit_type, variety, harvest_date, crop_code=cc3)

    now = datetime.datetime.now()
    harvest_datetime = datetime.datetime.combine(harvest_date, now.time()).strftime('%Y-%m-%d %H:%M:%S')
    
    data = {
        "Lot ID": lot_id_16, "Area Code": ac5, "Farmer ID": fm2, "Crop Code": cc3,
        "Contact Info": contact_info, "Fruit Type": fruit_type, "Variety": variety,
        "Harvest Date": harvest_date.strftime('%Y-%m-%d'),
        "Deliver Date": deliver_date.strftime('%Y-%m-%d'), "Storage Date": storage_date.strftime('%Y-%m-%d'),
        "Farming Method": farming_method, "Harvesting Number": harvesting_number,
        "Quantity": quantity, "Ag Practice": ag_practice
    }
    
    # --- [핵심] 무결성 보안 처리 구간 ---
    integrity_hash = calculate_hash(data)
    save_to_blockchain(integrity_hash, {"LotID": lot_id_16, "FarmerID": fm2, "CropCode": cc3, "Date": data["Harvest Date"]})
    current_data_cache = data.copy()

    try:
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        
        insert_query = """
        INSERT INTO qr (Lo, AC, FmID, LotID, CropCode, FrT, Vt, Ct, HD, DD, Qt, Mt, HN, Std, Rp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        db_data = (
            "A00", ac5, fm2, lot_id_16, cc3, fruit_type, variety, contact_info,
            harvest_datetime, deliver_date.strftime('%Y-%m-%d'),
            quantity, farming_method, harvesting_number, 
            storage_date.strftime('%Y-%m-%d'), ag_practice or None
        )
        cursor.execute(insert_query, db_data)
        db_connection.commit()
        
        cursor.close()
        db_connection.close()
        
        status_label_main_section.config(
            text=f"✅ A00 저장 완료 (LotID: {lot_id_16} / CC: {cc3})", 
            foreground="green"
        )
        
        generate_qr_code(data, lot_id_16)
        messagebox.showinfo("성공", f"A00 데이터가 저장되었습니다.\n16자리 LotID: {lot_id_16}\n작물코드: {cc3}\n(다음: QR 스캐너로 A01 창고 또는 A02 출하 스캔)")
        
    except mysql.connector.Error as err:
        status_label_main_section.config(text=f"Database error: {err}", foreground="red")

# --- [추가] 해킹 및 검증 시뮬레이션 함수 ---
def simulate_hack():
    """메모리에 있는 데이터를 강제로 조작"""
    if not current_data_cache:
        messagebox.showwarning("Warning", "No data saved yet to hack!")
        return
    
    # 데이터를 조작 (수량을 9999로 변경)
    current_data_cache["Quantity"] = "9999" 
    status_label_main_section.config(text="⚠️ Data Hacked! (Quantity -> 9999)", foreground="red")
    messagebox.showinfo("HACKED", "Data inside system has been tampered!\n(Quantity changed to 9999)")

def verify_data():
    """현재 데이터와 블록체인 기록을 대조하여 검증"""
    if not current_data_cache:
        messagebox.showwarning("Warning", "No data to verify!")
        return
    
    # 1. 현재 데이터의 해시 계산
    current_hash = calculate_hash(current_data_cache)
    
    # 2. 블록체인(파일)에서 최신 기록 로드
    stored_hash = None
    if os.path.exists(BLOCKCHAIN_FILE):
        with open(BLOCKCHAIN_FILE, "r", encoding="utf-8") as f:
            chain = json.load(f)
            if chain:
                stored_hash = chain[-1]["hash"] # 가장 최근 기록
    
    # 3. 비교
    if current_hash == stored_hash:
        status_label_main_section.config(text="✅ Verification Success: Data Integrity OK", foreground="blue")
        messagebox.showinfo("Verification", "✅ INTEGRITY VERIFIED\nData matches the blockchain record.")
    else:
        status_label_main_section.config(text="❌ Verification Failed: Data Modified!", foreground="red")
        messagebox.showerror("Verification", f"❌ ALERT: DATA TAMPERING DETECTED\n\nCurrent Hash: {current_hash[:10]}...\nStored Hash: {stored_hash[:10]}...")


# --- Validator Functions ---
def on_farmer_id_validate(char, entry_content): return char.isdigit() and len(entry_content) < 3
def validate_contact_info(char, current_text): return char.isdigit() or char == ""
def validate_numeric_input(char, current_text): return char.isdigit() or char == ""

def on_fruit_type_change(event):
    selected_fruit = fruit_type_combobox.get()
    variety_map = {
        "Apples": ["Hongro Apple", "Fuji Apple", "Gamhong Apple"],
        "Pears": ["Shingo Pear", "Wonhwang Pear", "Gamcheon Pear"],
        "Peaches": ["mibaegdo", "cheonjungdobaegdo", "yumyeongdo"],
        "Tangerines": ["eunju tangerine", "cheong tangerine", "mandarin"],
        "Melons": ["net melon", "baegja melon", "cham-oe"]
    }
    variety_combobox['values'] = variety_map.get(selected_fruit, [])

# --- GUI Setup ---
root = tk.Tk()
root.title("A00 Farm Data Collection (with Integrity Layer)")
root.geometry("1120x880")
root.configure(bg="#f3f4f6")
root.resizable(True, True)

# --- Modern Style Configuration (Premium Light Theme) ---
style = ttk.Style()
style.theme_use("clam")

# Color Palette Definitions
BG_COLOR = "#f3f4f6"     # Soft modern cool grey background
CARD_BG = "#ffffff"      # Elegant pure white card background
TEXT_COLOR = "#1f2937"   # Premium deep grey/charcoal for highly readable body text
ACCENT_BLUE = "#1a73e8"  # Google/Material Blue
ACCENT_GREEN = "#10b981" # Soft emerald green for primary actions
ACCENT_DARK = "#111827"  # Deep charcoal for headings/titles

# Background and Frame Styles
style.configure("TFrame", background=BG_COLOR)
style.configure("Card.TFrame", background=CARD_BG, relief="flat", borderwidth=0)
style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 11))
style.configure("Header.TLabel", background=CARD_BG, foreground=ACCENT_BLUE, font=("Segoe UI", 13, "bold"))
style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT_COLOR, font=("Segoe UI", 11))
style.configure("Title.TLabel", background=BG_COLOR, foreground=ACCENT_DARK, font=("Segoe UI", 22, "bold"))

# Button Styles
style.configure("TButton", font=("Segoe UI", 11, "bold"), background=ACCENT_BLUE, foreground="white", borderwidth=0, focuscolor="none")
style.map("TButton", background=[("active", "#1557b0")])

style.configure("Action.TButton", font=("Segoe UI", 12, "bold"), background=ACCENT_GREEN, foreground="white")
style.map("Action.TButton", background=[("active", "#059669")])

# Notebook / Tabs
style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
style.configure("TNotebook.Tab", background="#e5e7eb", foreground=TEXT_COLOR, padding=[15, 5], font=("Segoe UI", 10))
style.map("TNotebook.Tab", background=[("selected", BG_COLOR)], foreground=[("selected", ACCENT_BLUE)])

# Combobox and Entry
style.configure("TCombobox", fieldbackground="#ffffff", background="#ffffff", foreground=TEXT_COLOR, arrowcolor=ACCENT_BLUE, bordercolor="#e5e7eb", lightcolor="#e5e7eb", darkcolor="#e5e7eb")
style.map("TCombobox", 
    fieldbackground=[("readonly", "#ffffff")], 
    foreground=[("readonly", TEXT_COLOR)],
    selectbackground=[("readonly", "#ffffff")],
    selectforeground=[("readonly", TEXT_COLOR)]
)

style.configure("TEntry", fieldbackground="#ffffff", foreground=TEXT_COLOR, insertcolor=TEXT_COLOR, bordercolor="#e5e7eb", lightcolor="#e5e7eb", darkcolor="#e5e7eb")

validate_numeric_cmd = root.register(validate_numeric_input)

# Title Label at the top
title_label = ttk.Label(root, text="🛡️  FARM Information", style="Title.TLabel", anchor="center")
title_label.pack(pady=(20, 10))

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

main_section_frame = ttk.Frame(notebook, style="TFrame")
main_section_frame.pack(fill='both', expand=True)
notebook.add(main_section_frame, text="Main Data Entry")

# Frame 배치 (카드 스타일 적용)
frame1 = ttk.Frame(main_section_frame, style="Card.TFrame", padding=15)
frame1.place(x=20, y=20, width=530, height=340)
frame2 = ttk.Frame(main_section_frame, style="Card.TFrame", padding=15)
frame2.place(x=560, y=20, width=530, height=340)
frame3 = ttk.Frame(main_section_frame, style="Card.TFrame", padding=15)
frame3.place(x=20, y=370, width=530, height=340)
frame4 = ttk.Frame(main_section_frame, style="Card.TFrame", padding=15)
frame4.place(x=560, y=370, width=530, height=340)

# 타이틀 (Card Header Style)
ttk.Label(frame1, text="FARMER INFO", style="Header.TLabel", anchor="w").place(x=0, y=0, width=500, height=35)
ttk.Label(frame2, text="HARVEST LOGISTICS", style="Header.TLabel", anchor="w").place(x=0, y=0, width=500, height=35)
ttk.Label(frame3, text="CULTIVATION DETAILS", style="Header.TLabel", anchor="w").place(x=0, y=0, width=500, height=35)
ttk.Label(frame4, text="VERIFICATION & OUTPUT", style="Header.TLabel", anchor="w").place(x=0, y=0, width=500, height=35)

# --- Frame 1~3 위젯들 (기존 코드와 동일하게 복원) ---
# Frame 1
ttk.Label(frame1, text="Farmer ID", style="Card.TLabel").place(x=10, y=45, width=130, height=30)
validate_id = root.register(on_farmer_id_validate)
farmer_id_entry = ttk.Entry(frame1, font=("Segoe UI", 11), justify='center', validate="key", validatecommand=(validate_id, "%S", "%P"))
farmer_id_entry.place(x=150, y=45, width=350, height=30)

ttk.Label(frame1, text="Area Code", style="Card.TLabel").place(x=10, y=85, width=130, height=30)
area_code_combobox = ttk.Combobox(frame1, values=zip_codes, state="readonly", font=("Segoe UI", 11), justify='center')
area_code_combobox.place(x=150, y=85, width=350, height=30)

ttk.Label(frame1, text="Contact Info", style="Card.TLabel").place(x=10, y=125, width=130, height=30)
validate_contact_info_cmd = root.register(validate_contact_info)
contact_info_entry = ttk.Entry(frame1, font=("Segoe UI", 11), justify='center', validate="key", validatecommand=(validate_contact_info_cmd, "%S", "%P"))
contact_info_entry.place(x=150, y=125, width=350, height=30)
contact_info_entry.bind("<KeyRelease>", lambda event: format_phone_number(contact_info_entry))

# Frame 2
ttk.Label(frame2, text="Harvest Date", style="Card.TLabel").place(x=10, y=45, width=130, height=30)
harvest_date_picker = DateEntry(frame2, font=("Segoe UI", 11), width=20, justify='center',
                                background=ACCENT_BLUE, foreground="white", bordercolor="#e5e7eb",
                                headersbackground="#f3f4f6", headersforeground=TEXT_COLOR,
                                selectbackground=ACCENT_BLUE, selectforeground="white")
harvest_date_picker.place(x=150, y=45, width=350, height=30)

ttk.Label(frame2, text="Harvesting No.", style="Card.TLabel").place(x=10, y=85, width=130, height=30)
harvesting_number_entry = ttk.Entry(frame2, font=("Segoe UI", 11), justify='center', validate="key", validatecommand=(validate_numeric_cmd, "%S", "%P"))
harvesting_number_entry.place(x=150, y=85, width=350, height=30)

ttk.Label(frame2, text="Storage Date", style="Card.TLabel").place(x=10, y=125, width=130, height=30)
storage_date_picker = DateEntry(frame2, font=("Segoe UI", 11), width=20, justify='center',
                                background=ACCENT_BLUE, foreground="white", bordercolor="#e5e7eb",
                                headersbackground="#f3f4f6", headersforeground=TEXT_COLOR,
                                selectbackground=ACCENT_BLUE, selectforeground="white")
storage_date_picker.place(x=150, y=125, width=350, height=30)

ttk.Label(frame2, text="Delivery Date", style="Card.TLabel").place(x=10, y=165, width=130, height=30)
deliver_date_picker = DateEntry(frame2, font=("Segoe UI", 11), width=20, justify='center',
                                background=ACCENT_BLUE, foreground="white", bordercolor="#e5e7eb",
                                headersbackground="#f3f4f6", headersforeground=TEXT_COLOR,
                                selectbackground=ACCENT_BLUE, selectforeground="white")
deliver_date_picker.place(x=150, y=165, width=350, height=30)

ttk.Label(frame2, text="Quantity(box)", style="Card.TLabel").place(x=10, y=205, width=130, height=30)
quantity_entry = ttk.Entry(frame2, font=("Segoe UI", 11), justify='center', validate="key", validatecommand=(validate_numeric_cmd, "%S", "%P"))
quantity_entry.place(x=150, y=205, width=350, height=30)

# Frame 3
ttk.Label(frame3, text="Fruit Type", style="Card.TLabel").place(x=10, y=45, width=130, height=30)
fruit_type_combobox = ttk.Combobox(frame3, values=fruit_types, state="readonly", font=("Segoe UI", 11), justify='center')
fruit_type_combobox.place(x=150, y=45, width=350, height=30)
fruit_type_combobox.bind("<<ComboboxSelected>>", on_fruit_type_change)

ttk.Label(frame3, text="Variety", style="Card.TLabel").place(x=10, y=85, width=130, height=30)
variety_combobox = ttk.Combobox(frame3, state="readonly", font=("Segoe UI", 11), justify='center')
variety_combobox.place(x=150, y=85, width=350, height=30)

ttk.Label(frame3, text="Farming Method", style="Card.TLabel").place(x=10, y=125, width=130, height=30)
farming_method_combobox = ttk.Combobox(frame3, values=farming_methods, state="readonly", font=("Segoe UI", 11), justify='center')
farming_method_combobox.place(x=150, y=125, width=350, height=30)

ttk.Label(frame3, text="Ag Practice", style="Card.TLabel").place(x=10, y=165, width=130, height=30)
ag_practice_entry = ttk.Entry(frame3, font=("Segoe UI", 11), justify='center')
ag_practice_entry.place(x=150, y=165, width=350, height=30)

# --- [수정] Frame 4 (Result & Verification) ---
qr_label = ttk.Label(frame4, background=CARD_BG)
qr_label.place(relx=0.5, y=40, width=150, height=150, anchor="n")

# [수정] Save 버튼 중앙 정렬
# relx=0.5: 부모 프레임의 가로 50% 지점에 배치
# anchor="n": 버튼의 '북쪽(상단) 가운데'를 기준점으로 삼음 (즉, 정중앙 정렬됨)
save_button = ttk.Button(frame4, text="🚀 SAVE (DB + BLOCKCHAIN)", style="Action.TButton", command=save_all_formats)
save_button.place(relx=0.5, y=210, width=300, height=45, anchor="n")

# [추가] Hack 버튼
#hack_button = ttk.Button(frame4, text="😈 Hack Data", command=simulate_hack)
#hack_button.place(x=300, y=200, width=200, height=40)

# [추가] Verify 버튼
#verify_button = ttk.Button(frame4, text="🔍 Verify Integrity", command=verify_data)
#verify_button.place(x=50, y=250, width=450, height=40)

# 상태 메시지도 중앙 정렬
status_label_main_section = ttk.Label(frame4, text="", style="TLabel", anchor="center")
status_label_main_section.place(relx=0.5, y=300, width=450, height=30, anchor="n")

# XML Path Label (기존 유지)
def display_xml_path(file_path):
    xml_path_label = ttk.Label(frame4, text=f"Saved XML: {file_path}", font=("Segoe UI", 10, "underline"), foreground=ACCENT_BLUE, background=CARD_BG, cursor="hand2")
    xml_path_label.place(x=100, y=190, width=350, height=30)
    xml_path_label.bind("<Button-1>", lambda e: os.startfile(os.path.abspath(file_path)))

root.mainloop()