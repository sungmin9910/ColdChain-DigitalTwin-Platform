"""
ColdChain DigitalTwin Platform - Supply Chain v4 Specification (SSOT)
---------------------------------------------------------------------
1. 17-digit Unified Lot ID Standard (v4):
   LotID (17 digits) = AreaCode(5) + FmID(3) + CropCode(3, aT KAMIS) + HarvestDate(6, YYMMDD)
   Example: 55630 + 001 + 411 + 261124 = 55630001411261124

2. aT (KAMIS) Official 3-Digit Agricultural Commodity Codes:
   - 411: Apples (사과)
   - 412: Pears (배)
   - 413: Peaches (복숭아)
   - 415: Tangerines (감귤)
   - 222: Korean Melon / Cham-oe (참외)
   - 223: Melon (멜론: net melon, baegja melon)

3. v4 Cold-Chain Stage Flow (A01 ~ B05, C10 ~ D10):
   A01 (농가 수확·무색QR)
     -> [A02 농가 저장고 들어감 (선택) -> A03 농가 저장고 나옴 (선택)]
     -> A04 (농가 출하·APC로 출발, 1구간 출발)
     -> B01 (APC 입고, 1구간 도착)
     -> B02 (APC 선별·유색QR 변경)
     -> [B03 APC 저장고 들어감 (선택) -> B04 APC 저장고 나옴 (선택)]
     -> B05 (APC 출하, 2구간 출발)
     -> C10 (유통 창고 저장, 2구간 도착)
     -> C11 (유통 출하·판매처 출발, 3구간 출발)
     -> D10 (판매처 도착, 3구간 도착)

   * Backward-compatible with legacy v3 (16-digit, A00~D10) and v2 (A00~A16) lots.
"""

import re
from datetime import datetime, date

# ---------------------------------------------------------------------
# 0. Area Code (5-Digit Postal Code) Master: 무진장 (장수 5 · 무주 5 · 진안 5)
# ---------------------------------------------------------------------
AREA_CODE_OPTIONS = [
    # 장수군 (5)
    {"code": "55630", "region": "장수", "label_ko": "55630 (장수 장수읍)", "label_en": "55630 (Jangsu-eup, Jangsu)", "name_ko": "전북 장수군 (장수읍)", "name_en": "Jangsu-eup, Jangsu-gun, Jeonbuk", "coords": (35.6470, 127.5210)},
    {"code": "55631", "region": "장수", "label_ko": "55631 (장수 산서면)", "label_en": "55631 (Sanseo, Jangsu)", "name_ko": "전북 장수군 (산서면)", "name_en": "Sanseo-myeon, Jangsu-gun, Jeonbuk", "coords": (35.6170, 127.4220)},
    {"code": "55632", "region": "장수", "label_ko": "55632 (장수 번암면)", "label_en": "55632 (Beonam, Jangsu)", "name_ko": "전북 장수군 (번암면)", "name_en": "Beonam-myeon, Jangsu-gun, Jeonbuk", "coords": (35.5390, 127.5530)},
    {"code": "55633", "region": "장수", "label_ko": "55633 (장수 장계면)", "label_en": "55633 (Janggye, Jangsu)", "name_ko": "전북 장수군 (장계면)", "name_en": "Janggye-myeon, Jangsu-gun, Jeonbuk", "coords": (35.7270, 127.5850)},
    {"code": "55634", "region": "장수", "label_ko": "55634 (장수 천천면)", "label_en": "55634 (Cheoncheon, Jangsu)", "name_ko": "전북 장수군 (천천면)", "name_en": "Cheoncheon-myeon, Jangsu-gun, Jeonbuk", "coords": (35.7070, 127.4810)},
    # 무주군 (5)
    {"code": "55518", "region": "무주", "label_ko": "55518 (무주 무주읍)", "label_en": "55518 (Muju-eup, Muju)", "name_ko": "전북 무주군 (무주읍)", "name_en": "Muju-eup, Muju-gun, Jeonbuk", "coords": (36.0068, 127.6608)},
    {"code": "55549", "region": "무주", "label_ko": "55549 (무주 설천면)", "label_en": "55549 (Seolcheon, Muju)", "name_ko": "전북 무주군 (설천면)", "name_en": "Seolcheon-myeon, Muju-gun, Jeonbuk", "coords": (36.0170, 127.7830)},
    {"code": "55527", "region": "무주", "label_ko": "55527 (무주 적상면)", "label_en": "55527 (Jeoksang, Muju)", "name_ko": "전북 무주군 (적상면)", "name_en": "Jeoksang-myeon, Muju-gun, Jeonbuk", "coords": (35.9510, 127.6480)},
    {"code": "55540", "region": "무주", "label_ko": "55540 (무주 안성면)", "label_en": "55540 (Anseong, Muju)", "name_ko": "전북 무주군 (안성면)", "name_en": "Anseong-myeon, Muju-gun, Jeonbuk", "coords": (35.8750, 127.6560)},
    {"code": "55559", "region": "무주", "label_ko": "55559 (무주 무풍면)", "label_en": "55559 (Mupung, Muju)", "name_ko": "전북 무주군 (무풍면)", "name_en": "Mupung-myeon, Muju-gun, Jeonbuk", "coords": (35.9560, 127.8480)},
    # 진안군 (5)
    {"code": "55435", "region": "진안", "label_ko": "55435 (진안 진안읍)", "label_en": "55435 (Jinan-eup, Jinan)", "name_ko": "전북 진안군 (진안읍)", "name_en": "Jinan-eup, Jinan-gun, Jeonbuk", "coords": (35.7906, 127.4229)},
    {"code": "55451", "region": "진안", "label_ko": "55451 (진안 마령면)", "label_en": "55451 (Maryeong, Jinan)", "name_ko": "전북 진안군 (마령면)", "name_en": "Maryeong-myeon, Jinan-gun, Jeonbuk", "coords": (35.7470, 127.3670)},
    {"code": "55455", "region": "진안", "label_ko": "55455 (진안 백운면)", "label_en": "55455 (Baegun, Jinan)", "name_ko": "전북 진안군 (백운면)", "name_en": "Baegun-myeon, Jinan-gun, Jeonbuk", "coords": (35.6980, 127.4190)},
    {"code": "55459", "region": "진안", "label_ko": "55459 (진안 성수면)", "label_en": "55459 (Seongsu, Jinan)", "name_ko": "전북 진안군 (성수면)", "name_en": "Seongsu-myeon, Jinan-gun, Jeonbuk", "coords": (35.6940, 127.3390)},
    {"code": "55416", "region": "진안", "label_ko": "55416 (진안 부귀면)", "label_en": "55416 (Bugwi, Jinan)", "name_ko": "전북 진안군 (부귀면)", "name_en": "Bugwi-myeon, Jinan-gun, Jeonbuk", "coords": (35.8140, 127.3450)},
]

AREA_CODE_INFO = {
    item["code"]: {"ko": item["name_ko"], "en": item["name_en"], "coords": item["coords"]}
    for item in AREA_CODE_OPTIONS
}
AREA_CODE_INFO.update({
    # 기존/군청 대표 코드 하위 호환 유지
    "55635": {"ko": "전북 장수군 (계남면)", "en": "Gyenam-myeon, Jangsu-gun, Jeonbuk", "coords": (35.6960, 127.5750)},
    "55517": {"ko": "전북 무주군 (무주읍)", "en": "Muju-eup, Muju-gun, Jeonbuk", "coords": (36.0068, 127.6608)},
    "55434": {"ko": "전북 진안군 (진안읍)", "en": "Jinan-eup, Jinan-gun, Jeonbuk", "coords": (35.7906, 127.4229)},
})

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


def normalize_fmid_3digit(farmer_id: str) -> str:
    """농가번호(FmID)를 3자리 숫자(001~999)로 정규화합니다."""
    digits = re.sub(r"\D", "", str(farmer_id or ""))
    if not digits:
        return "001"
    return digits[-3:].zfill(3)


def format_yymmdd(harvest_date) -> str:
    if isinstance(harvest_date, (datetime, date)):
        return harvest_date.strftime("%y%m%d")
    s = re.sub(r"\D", "", str(harvest_date or ""))
    if len(s) >= 8:  # YYYYMMDD...
        return s[2:8]
    if len(s) == 6:  # YYMMDD
        return s
    return datetime.now().strftime("%y%m%d")


def build_lot_id_17(
    area_code: str,
    farmer_id: str,
    fruit_type: str = "Apples",
    variety: str = "",
    harvest_date=None,
    crop_code: str = None,
) -> str:
    """v4: AreaCode(5) + FmID(3) + CropCode(3) + HarvestDate(6, YYMMDD) = 17자리 통합 코드 생성"""
    ac5 = normalize_area_code(area_code)
    fm3 = normalize_fmid_3digit(farmer_id)
    cc3 = re.sub(r"\D", "", str(crop_code or ""))[:3].zfill(3) if crop_code else get_crop_code(fruit_type, variety)
    hd6 = format_yymmdd(harvest_date)
    return f"{ac5}{fm3}{cc3}{hd6}"


def build_lot_id_16(
    area_code: str,
    farmer_id: str,
    fruit_type: str = "Apples",
    variety: str = "",
    harvest_date=None,
    crop_code: str = None,
) -> str:
    """v3 레거시 호환: AreaCode(5) + FmID(2) + CropCode(3) + HarvestDate(6, YYMMDD) = 16자리 통합 코드 생성"""
    ac5 = normalize_area_code(area_code)
    fm2 = normalize_fmid_2digit(farmer_id)
    cc3 = re.sub(r"\D", "", str(crop_code or ""))[:3].zfill(3) if crop_code else get_crop_code(fruit_type, variety)
    hd6 = format_yymmdd(harvest_date)
    return f"{ac5}{fm2}{cc3}{hd6}"


def is_v4_lot_id(lot_id: str) -> bool:
    s = str(lot_id or "").strip()
    return len(s) == 17 and s.isdigit()


def is_v3_lot_id(lot_id: str) -> bool:
    s = str(lot_id or "").strip()
    return len(s) == 16 and s.isdigit()


def is_modern_lot_id(lot_id: str) -> bool:
    """17자리(v4) 또는 16자리(v3) 표준 LotID 여부"""
    return is_v4_lot_id(lot_id) or is_v3_lot_id(lot_id)


def parse_lot_id(lot_id: str):
    """17자리(v4: AC5+FmID3+CC3+YYMMDD6) 또는 16자리(v3: AC5+FmID2+CC3+YYMMDD6) LotID를 분해합니다."""
    s = str(lot_id or "").strip()
    if is_v4_lot_id(s):
        ac5 = s[0:5]
        fm = s[5:8]
        cc3 = s[8:11]
        yymmdd = s[11:17]
        ver = "v4"
    elif is_v3_lot_id(s):
        ac5 = s[0:5]
        fm = s[5:7]
        cc3 = s[7:10]
        yymmdd = s[10:16]
        ver = "v3"
    else:
        return None
    iso_date = f"20{yymmdd[0:2]}-{yymmdd[2:4]}-{yymmdd[4:6]}"
    crop_info = CROP_INFO_BY_CODE.get(cc3, {"ko": "과일", "en": "Fruit", "fruit_type": "Apples"})
    return {
        "lot_id": s,
        "protocol_ver": ver,
        "area_code": ac5,
        "farmer_code": fm,
        "crop_code": cc3,
        "yymmdd": yymmdd,
        "harvest_date_iso": iso_date,
        "crop_ko": crop_info["ko"],
        "crop_en": crop_info["en"],
        "fruit_type": crop_info["fruit_type"],
    }


def parse_lot_id_16(lot_id: str):
    """하위 호환 래퍼: 17자리(v4) 및 16자리(v3) 모두 분해 지원"""
    return parse_lot_id(lot_id)


# ---------------------------------------------------------------------
# 2. Supply Chain Stage Codes
#    - v4 (Current): A01~A04, B01~B05, C10~D10 (17-digit LotID, 3-digit FmID)
#    - v3 (Legacy) : A00~A02, B10~B13, C10~D10 (16-digit LotID, 2-digit FmID)
#    - v2 (Legacy) : A00~A16
# ---------------------------------------------------------------------
V4_STAGE_ORDER = ["A01", "A02", "A03", "A04", "B01", "B02", "B03", "B04", "B05", "C10", "C11", "D10"]
V4_DB_STAGES = set(V4_STAGE_ORDER)
V4_RAW_QR_STAGES = {"A01", "A02", "A03", "A04", "B01", "B02"}   # 무색 QR 대상 (농가 수확~APC 입고·선별)
V4_COLORED_QR_STAGES = {"B03", "B04", "B05", "C10", "C11", "D10"}  # 유색 QR 대상 (선별 후 저장~판매처)
V4_STORAGE_STAGES = {"A02", "A03", "B03", "B04", "C10"}         # 저장고 입·출고 온습도 기록 단계
V4_OPTIONAL_STAGES = {"A02", "A03", "B03", "B04"}
V4_SCANNER_MODES = ["AUTO", "A02", "A03", "A04", "B01", "B03", "B04", "B05", "C10", "C11", "D10"]
V4_ONLY_STAGES = {"A03", "A04", "B01", "B02", "B03", "B04", "B05"}

V3_STAGE_ORDER = ["A00", "A01", "A02", "B10", "B12_PRE", "B11", "B12_POST", "B13", "C10", "C11", "D10"]
V3_DB_STAGES = {"A00", "A01", "A02", "B10", "B11", "B12", "B13", "C10", "C11", "D10"}
V3_RAW_QR_STAGES = {"A00", "A01", "A02", "B10", "B11"}
V3_COLORED_QR_STAGES = {"B13", "C10", "C11", "D10"}
V3_STORAGE_STAGES = {"A01", "B12", "C10"}
V3_OPTIONAL_STAGES = {"A01", "B12", "B12_PRE", "B12_POST"}
V3_SCANNER_MODES = ["AUTO", "A01", "A02", "B10", "B12", "B13", "C10", "C11", "D10"]
V3_ONLY_STAGES = {"B10", "B11", "B12", "B13"}

V2_LEGACY_STAGE_ORDER = ["A00", "A01", "A02", "A10", "A11", "A12", "A13", "A14", "A15", "A16"]
V2_ONLY_STAGES = {"A10", "A11", "A12", "A13", "A14", "A15", "A16"}

V4_STAGE_META = {
    "KO": {
        "A01": ("🌱 농가 수확 (A01)", "산지 농가에서 수확하고 17자리 고유 코드 기반 안심 QR을 발급했습니다."),
        "A02": ("🏡 농가 저장고 입고 (A02)", "수확 직후 농가 저온저장고에 입고되어 예냉 및 신선 보관을 시작했습니다."),
        "A03": ("📤 농가 저장고 출고 (A03)", "농가 저온저장고 보관을 마치고 출하 준비를 위해 출고되었습니다."),
        "A04": ("🚜 농가 출하 · APC 출발 (A04)", "농가에서 산지유통센터(APC)로 1구간 운송을 출발했습니다."),
        "B01": ("🏢 APC 입고 (B01)", "산지유통센터(APC)에 신선한 상태로 입고되었습니다."),
        "B02": ("🔍 APC 선별 · 유색QR 변경 (B02)", "품질·등급을 엄격하게 선별하고 등급별 유색 QR 코드로 교체했습니다."),
        "B03": ("❄️ APC 저장고 입고 (B03)", "선별 완료 상품을 APC 저온저장고에 입고하여 최적 온습도로 보관합니다."),
        "B04": ("📦 APC 저장고 출고 (B04)", "APC 저온저장고 보관을 마치고 출하를 위해 출고되었습니다."),
        "B05": ("🚛 APC 출하 (B05)", "APC에서 유통 창고를 향해 2구간 냉장 운송을 출발했습니다."),
        "C10": ("🏬 유통 창고 저장 (C10)", "유통 물류센터 저온창고에 도착하여 안전하게 보관 중입니다."),
        "C11": ("🚚 유통 출하 · 판매처 출발 (C11)", "유통 창고에서 최종 판매처로 3구간 냉장 배송을 출발했습니다."),
        "D10": ("🏪 판매처 도착 (D10)", "전 구간 콜드체인 안전 운송을 마치고 판매처에 신선하게 도착했습니다!"),
    },
    "EN": {
        "A01": ("🌱 Farm Harvest (A01)", "Harvested at the farm and issued a 17-digit traceable raw QR code."),
        "A02": ("🏡 Farm Storage In (A02)", "Entered farm cold storage for pre-cooling and freshness preservation."),
        "A03": ("📤 Farm Storage Out (A03)", "Exited farm cold storage and prepared for dispatch."),
        "A04": ("🚜 Farm Dispatch to APC (A04)", "Departed from the farm toward the APC center (Leg 1 transport)."),
        "B01": ("🏢 APC Receiving (B01)", "Arrived fresh at the Agricultural Products Processing Center (APC)."),
        "B02": ("🔍 APC Sorting & Colored QR (B02)", "Strictly graded and upgraded to color-coded grade QR labels."),
        "B03": ("❄️ APC Storage In (B03)", "Entered APC cold storage under optimal temperature & humidity control."),
        "B04": ("📦 APC Storage Out (B04)", "Exited APC cold storage for distribution dispatch."),
        "B05": ("🚛 APC Dispatch (B05)", "Departed from APC toward the distribution warehouse (Leg 2 transport)."),
        "C10": ("🏬 Distribution Storage (C10)", "Arrived and stored safely in the distribution center cold warehouse."),
        "C11": ("🚚 Distribution Dispatch (C11)", "Dispatched from distribution warehouse to the retail store (Leg 3 transport)."),
        "D10": ("🏪 Retail Arrival (D10)", "Safely arrived at the retail store with verified end-to-end cold-chain!"),
    },
}

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
    """해당 로트가 v4(17자리, A01~B05·C10~D10), v3(16자리, A00~D10), v2(A00~A16) 중 어느 프로토콜인지 판별합니다."""
    codes = set(stage_codes or [])
    if codes & V4_ONLY_STAGES:
        return "v4"
    if is_v4_lot_id(lot_id):
        return "v4"
    if codes & V3_ONLY_STAGES:
        return "v3"
    if is_v3_lot_id(lot_id):
        return "v3"
    if codes & V2_ONLY_STAGES:
        return "v2"
    if explicit_ver in ("v2", "v3", "v4"):
        return explicit_ver
    return "v2"
