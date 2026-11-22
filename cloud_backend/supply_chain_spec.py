"""
ColdChain DigitalTwin Platform - Supply Chain v3 Specification (SSOT)
---------------------------------------------------------------------
1. 16-digit Unified Lot ID Standard:
   LotID (16 digits) = AreaCode(5) + FmID(2) + CropCode(3, aT KAMIS) + HarvestDate(6, YYMMDD)
   Example: 55632 + 07 + 411 + 261122 = 5563207411261122

2. aT (KAMIS) Official 3-Digit Agricultural Commodity Codes:
   - 411: Apples (사과)
   - 412: Pears (배)
   - 413: Peaches (복숭아)
   - 415: Tangerines (감귤)
   - 222: Korean Melon / Cham-oe (참외)
   - 223: Melon (멜론: net melon, baegja melon)

3. v3 Flexible Cold-Chain Stage Flow (A00 ~ D10):
   A00 (농가 수확·무색QR)
     -> [A01 농가창고 (선택)] -> A02 (농가 출하, 1구간 출발)
     -> B10 (APC 입고, 1구간 도착)
     -> [B12 APC창고 선별전 (선택)]
     -> B11 (APC 선별·유색QR 변경)
     -> [B12 APC창고 선별후 (선택)]
     -> B13 (APC 출하, 2구간 출발)
     -> C10 (유통 창고 저장, 2구간 도착)
     -> C11 (유통 출하·판매처 출발, 3구간 출발)
     -> D10 (판매처 도착, 3구간 도착)

   * Backward-compatible with legacy v2 (A00 ~ A16) lots.
"""

import re
from datetime import datetime, date

# ---------------------------------------------------------------------
# 0. Area Code (5-Digit Postal Code) Master: 무진장 (장수 · 무주 · 진안)
# ---------------------------------------------------------------------
AREA_CODE_OPTIONS = [
    {"code": "55630", "label_ko": "55630 (장수)", "label_en": "55630 (Jangsu)", "name_ko": "전북 장수군", "name_en": "Jangsu-gun, Jeonbuk", "coords": (35.647, 127.521)},
    {"code": "55517", "label_ko": "55517 (무주)", "label_en": "55517 (Muju)", "name_ko": "전북 무주군", "name_en": "Muju-gun, Jeonbuk", "coords": (36.0068, 127.6608)},
    {"code": "55434", "label_ko": "55434 (진안)", "label_en": "55434 (Jinan)", "name_ko": "전북 진안군", "name_en": "Jinan-gun, Jeonbuk", "coords": (35.7906, 127.4229)},
]

AREA_CODE_INFO = {
    "55630": {"ko": "전북 장수군", "en": "Jangsu-gun, Jeonbuk", "coords": (35.647, 127.521)},
    "55517": {"ko": "전북 무주군", "en": "Muju-gun, Jeonbuk", "coords": (36.0068, 127.6608)},
    "55434": {"ko": "전북 진안군", "en": "Jinan-gun, Jeonbuk", "coords": (35.7906, 127.4229)},
    # 기존 장수군 읍·면 하위 호환 유지
    "55631": {"ko": "전북 장수군 (산서면)", "en": "Sanseo-myeon, Jangsu-gun, Jeonbuk", "coords": (35.617, 127.422)},
    "55632": {"ko": "전북 장수군 (번암면)", "en": "Beonam-myeon, Jangsu-gun, Jeonbuk", "coords": (35.539, 127.553)},
    "55633": {"ko": "전북 장수군 (장계면)", "en": "Janggye-myeon, Jangsu-gun, Jeonbuk", "coords": (35.727, 127.585)},
    "55634": {"ko": "전북 장수군 (천천면)", "en": "Cheoncheon-myeon, Jangsu-gun, Jeonbuk", "coords": (35.707, 127.481)},
    "55635": {"ko": "전북 장수군 (계남면)", "en": "Gyenam-myeon, Jangsu-gun, Jeonbuk", "coords": (35.696, 127.575)},
}

# ---------------------------------------------------------------------
# 1. aT (KAMIS) 3-Digit Crop Codes
# ---------------------------------------------------------------------
CROP_CODE_BY_FRUIT = {
    "Apples": "411",
    "Pears": "412",
    "Peaches": "413",
    "Tangerines": "415",
    "Melons": "222",  # default for Melons; refined by variety below (222 참외 / 223 멜론)
}

CROP_CODE_BY_VARIETY = {
    "cham-oe": "222",
    "참외": "222",
    "korean melon": "222",
    "net melon": "223",
    "baegja melon": "223",
    "멜론": "223",
}

CROP_INFO_BY_CODE = {
    "411": {"ko": "사과", "en": "Apple", "fruit_type": "Apples"},
    "412": {"ko": "배", "en": "Pear", "fruit_type": "Pears"},
    "413": {"ko": "복숭아", "en": "Peach", "fruit_type": "Peaches"},
    "415": {"ko": "감귤", "en": "Tangerine", "fruit_type": "Tangerines"},
    "222": {"ko": "참외", "en": "Korean Melon", "fruit_type": "Melons"},
    "223": {"ko": "멜론", "en": "Melon", "fruit_type": "Melons"},
}

VARIETY_OPTIONS = {
    "Apples": ["Fuji Apple", "Hongro Apple", "Gamhong Apple"],
    "Pears": ["Shingo Pear", "Wonhwang Pear", "Gamcheon Pear"],
    "Peaches": ["mibaegdo", "cheonjungdobaegdo", "yumyeongdo"],
    "Tangerines": ["eunju tangerine", "cheong tangerine", "mandarin"],
    "Melons": ["cham-oe", "net melon", "baegja melon"],
}


def get_crop_code(fruit_type: str, variety: str = "") -> str:
    """과일 품목(FrT)과 품종(Vt)을 기반으로 aT KAMIS 공식 3자리 작물 코드를 반환합니다."""
    vt_low = str(variety or "").replace("+", " ").strip().lower()
    for k, code in CROP_CODE_BY_VARIETY.items():
        if k in vt_low:
            return code

    frt_clean = str(fruit_type or "").replace("+", " ").strip()
    if frt_clean in CROP_CODE_BY_FRUIT:
        return CROP_CODE_BY_FRUIT[frt_clean]

    frt_low = frt_clean.lower()
    if "apple" in frt_low or "사과" in frt_low:
        return "411"
    if "pear" in frt_low or "배" in frt_low:
        return "412"
    if "peach" in frt_low or "복숭아" in frt_low:
        return "413"
    if "tangerine" in frt_low or "감귤" in frt_low or "귤" in frt_low:
        return "415"
    if "참외" in frt_low or "cham" in frt_low:
        return "222"
    if "melon" in frt_low or "멜론" in frt_low:
        return "223"
    return "411"


def normalize_area_code(area_code: str) -> str:
    digits = re.sub(r"\D", "", str(area_code or ""))
    if not digits:
        return "55630"
    return digits[:5].zfill(5)


def normalize_fmid_2digit(farmer_id: str) -> str:
    digits = re.sub(r"\D", "", str(farmer_id or ""))
    if not digits:
        return "01"
    return digits[-2:].zfill(2)


def format_yymmdd(harvest_date) -> str:
    if isinstance(harvest_date, (datetime, date)):
        return harvest_date.strftime("%y%m%d")
    s = re.sub(r"\D", "", str(harvest_date or ""))
    if len(s) >= 8:  # YYYYMMDD...
        return s[2:8]
    if len(s) == 6:  # YYMMDD
        return s
    return datetime.now().strftime("%y%m%d")


def build_lot_id_16(
    area_code: str,
    farmer_id: str,
    fruit_type: str = "Apples",
    variety: str = "",
    harvest_date=None,
    crop_code: str = None,
) -> str:
    """AreaCode(5) + FmID(2) + CropCode(3) + HarvestDate(6, YYMMDD) = 16자리 통합 코드 생성"""
    ac5 = normalize_area_code(area_code)
    fm2 = normalize_fmid_2digit(farmer_id)
    cc3 = re.sub(r"\D", "", str(crop_code or ""))[:3].zfill(3) if crop_code else get_crop_code(fruit_type, variety)
    hd6 = format_yymmdd(harvest_date)
    return f"{ac5}{fm2}{cc3}{hd6}"


def is_v3_lot_id(lot_id: str) -> bool:
    s = str(lot_id or "").strip()
    return len(s) == 16 and s.isdigit()


def parse_lot_id_16(lot_id: str):
    """16자리 LotID를 AreaCode(5), FmID(2), CropCode(3), YYMMDD(6)로 분해합니다."""
    s = str(lot_id or "").strip()
    if not is_v3_lot_id(s):
        return None
    ac5 = s[0:5]
    fm2 = s[5:7]
    cc3 = s[7:10]
    yymmdd = s[10:16]
    iso_date = f"20{yymmdd[0:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}"
    crop_info = CROP_INFO_BY_CODE.get(cc3, {"ko": "과일", "en": "Fruit", "fruit_type": "Apples"})
    return {
        "lot_id": s,
        "area_code": ac5,
        "farmer_code": fm2,
        "crop_code": cc3,
        "yymmdd": yymmdd,
        "harvest_date_iso": iso_date,
        "crop_ko": crop_info["ko"],
        "crop_en": crop_info["en"],
        "fruit_type": crop_info["fruit_type"],
    }


# ---------------------------------------------------------------------
# 2. Supply Chain Stage Codes (v3: A00 ~ D10 & Legacy v2: A00 ~ A16)
# ---------------------------------------------------------------------
V3_STAGE_ORDER = ["A00", "A01", "A02", "B10", "B12_PRE", "B11", "B12_POST", "B13", "C10", "C11", "D10"]
V3_DB_STAGES = {"A00", "A01", "A02", "B10", "B11", "B12", "B13", "C10", "C11", "D10"}
V3_RAW_QR_STAGES = {"A00", "A01", "A02", "B10", "B11"}  # 무색 QR 대상 (+ 선별 전 B12)
V3_COLORED_QR_STAGES = {"B13", "C10", "C11", "D10"}     # 유색 QR 대상 (+ 선별 후 B12)
V3_STORAGE_STAGES = {"A01", "B12", "C10"}               # 창고 온습도 기록 단계
V3_OPTIONAL_STAGES = {"A01", "B12", "B12_PRE", "B12_POST"}
V3_SCANNER_MODES = ["AUTO", "A01", "A02", "B10", "B12", "B13", "C10", "C11", "D10"]

V2_LEGACY_STAGE_ORDER = ["A00", "A01", "A02", "A10", "A11", "A12", "A13", "A14", "A15", "A16"]
V2_ONLY_STAGES = {"A10", "A11", "A12", "A13", "A14", "A15", "A16"}

V3_STAGE_META = {
    "KO": {
        "A00": ("🌱 농가 수확 (A00)", "산지 농가에서 수확하고 16자리 고유 코드 기반 안심 QR을 발급했습니다."),
        "A01": ("🏡 농가 창고 보관 (A01)", "수확 직후 농가 저온창고에서 예냉 및 신선 보관을 진행했습니다."),
        "A02": ("🚜 농가 출하 (A02)", "농가에서 산지유통센터(APC)로 1구간 운송을 시작했습니다."),
        "B10": ("🏢 APC 입고 (B10)", "산지유통센터(APC)에 신선한 상태로 입고되었습니다."),
        "B12_PRE": ("❄️ APC 창고 · 선별 전 (B12)", "선별 전 APC 저온창고에서 최적 온습도로 원물을 보관했습니다."),
        "B11": ("🔍 APC 선별 · 유색QR 변경 (B11)", "품질·등급을 엄격하게 선별하고 등급별 유색 QR 코드로 교체했습니다."),
        "B12_POST": ("❄️ APC 창고 · 선별 후 (B12)", "등급 선별 후 출하 전까지 APC 저온창고에 안전하게 보관했습니다."),
        "B12": ("❄️ APC 창고 (B12)", "APC 저온창고에서 최적의 온습도로 신선도를 유지하며 보관했습니다."),
        "B13": ("🚛 APC 출하 (B13)", "APC에서 유통 창고를 향해 2구간 냉장 운송을 시작했습니다."),
        "C10": ("🏬 유통 창고 저장 (C10)", "유통 물류센터 저온창고에 도착하여 안전하게 보관 중입니다."),
        "C11": ("🚚 유통 출하 · 판매처 출발 (C11)", "유통 창고에서 최종 판매처로 3구간 냉장 배송을 출발했습니다."),
        "D10": ("🏪 판매처 도착 (D10)", "전 구간 콜드체인 안전 운송을 마치고 판매처에 신선하게 도착했습니다!"),
    },
    "EN": {
        "A00": ("🌱 Farm Harvest (A00)", "Harvested at the farm and issued a 16-digit traceable raw QR code."),
        "A01": ("🏡 Farm Storage (A01)", "Pre-cooled and stored fresh at the farm's cold storage facility."),
        "A02": ("🚜 Farm Dispatch (A02)", "Departed from the farm toward the APC center (Leg 1 transport)."),
        "B10": ("🏢 APC Receiving (B10)", "Arrived fresh at the Agricultural Products Processing Center (APC)."),
        "B12_PRE": ("❄️ APC Storage · Pre-Sort (B12)", "Stored under optimal temperature & humidity in APC storage prior to sorting."),
        "B11": ("🔍 APC Sorting & Colored QR (B11)", "Strictly graded and upgraded to color-coded grade QR labels."),
        "B12_POST": ("❄️ APC Storage · Post-Sort (B12)", "Stored under cold-chain control in APC storage after grading."),
        "B12": ("❄️ APC Cold Storage (B12)", "Stored under optimal temperature & humidity at APC cold storage."),
        "B13": ("🚛 APC Dispatch (B13)", "Departed from APC toward the distribution warehouse (Leg 2 transport)."),
        "C10": ("🏬 Distribution Storage (C10)", "Arrived and stored safely in the distribution center cold warehouse."),
        "C11": ("🚚 Distribution Dispatch (C11)", "Dispatched from distribution warehouse to the retail store (Leg 3 transport)."),
        "D10": ("🏪 Retail Arrival (D10)", "Safely arrived at the retail store with verified end-to-end cold-chain!"),
    },
}

V2_STAGE_META = {
    "KO": {
        "A00": ("🌱 농장 수확", "정성껏 재배한 과일을 정직하게 수확했습니다."),
        "A01": ("🏡 농가 저온저장", "수확 직후 산지 저온저장고에서 예냉 및 신선 보관을 거쳤습니다."),
        "A02": ("🚜 산지 출하", "산지유통센터(APC)를 향해 안전하게 운송을 시작했습니다."),
        "A10": ("🏢 입고", "생산지에서 신선한 상태로 센터에 도착했습니다."),
        "A11": ("💦 세척", "깨끗하고 안전한 물로 세척 과정을 마쳤습니다."),
        "A12": ("🔍 선별", "크기와 당도, 품질을 엄격하게 선별했습니다."),
        "A13": ("📦 포장", "신선함을 유지할 수 있는 전용 패키지로 포장되었습니다."),
        "A14": ("❄️ 저장", "최적의 온도와 습도로 신선도를 보관 중입니다."),
        "A15": ("🚛 출하", "고객님을 만나기 위해 건강하게 출발했습니다!"),
        "A16": ("🏪 판매처 도착", "콜드체인 안전 운송을 마치고 판매처에 신선하게 도착했습니다!"),
    },
    "EN": {
        "A00": ("🌱 Harvest", "Carefully cultivated fruit has been honestly harvested."),
        "A01": ("🏡 Farm Cold Storage", "Pre-cooled and stored fresh at the farm's cold storage facility."),
        "A02": ("🚜 Farm Dispatch", "Departed safely from the farm toward the APC sorting center."),
        "A10": ("🏢 Receiving", "Arrived at the APC center in a fresh state from the farm."),
        "A11": ("💦 Washing", "Completed the washing process with clean and safe water."),
        "A12": ("🔍 Sorting", "Strictly sorted by size, sweetness, and quality."),
        "A13": ("📦 Packaging", "Packed in a specialized package to maintain freshness."),
        "A14": ("❄️ Storage", "Storing at optimal temperature and humidity to preserve freshness."),
        "A15": ("🚛 Shipping", "Healthy shipment has departed to meet the customer!"),
        "A16": ("🏪 Retail Arrival", "Safely arrived at the retail store via cold-chain transport!"),
    },
}


def detect_protocol_version(lot_id: str, stage_codes=None, explicit_ver: str = None) -> str:
    """해당 로트가 v3(16자리, A00~D10)인지 v2 레거시(A00~A16)인지 판별합니다."""
    codes = set(stage_codes or [])
    if codes & {"B10", "B11", "B12", "B13", "C10", "C11", "D10"}:
        return "v3"
    if codes & V2_ONLY_STAGES:
        return "v2"
    if explicit_ver in ("v2", "v3"):
        return explicit_ver
    return "v3" if is_v3_lot_id(lot_id) else "v2"
