import pymysql
import math
import random
from datetime import datetime, timedelta

# ----------------------------------------------------------------
# 1. DB 연결 설정 로더 (secrets.toml에서 파싱)
# ----------------------------------------------------------------
def get_db_connection():
    secrets_path = r"c:\Users\yuyub\Desktop\hsm\ColdChain-DigitalTwin-Platform\Final_Experiment\4_APC_Coldchain_Dashboard\.streamlit\secrets.toml"
    secrets = {}
    with open(secrets_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("[") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        secrets[key] = val

    host = secrets.get("MYSQL_HOST")
    port = int(secrets.get("MYSQL_PORT", 3306))
    user = secrets.get("MYSQL_USER")
    password = secrets.get("MYSQL_PASSWORD")
    database = secrets.get("MYSQL_DATABASE")

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

# ----------------------------------------------------------------
# 2. 경로 보간 (Interpolation) 함수
# ----------------------------------------------------------------
def interpolate_points(points, target_count):
    interpolated = []
    segments = len(points) - 1
    pts_per_segment = target_count // segments
    remainder = target_count % segments
    
    for i in range(segments):
        p1 = points[i]
        p2 = points[i+1]
        count = pts_per_segment + (1 if i < remainder else 0)
        for j in range(count):
            t = j / count
            lat = p1[0] + (p2[0] - p1[0]) * t
            lng = p1[1] + (p2[1] - p1[1]) * t
            
            # 미세한 GPS 잡음 추가 (소수점 6째 자리 수준)
            lat += random.uniform(-0.00003, 0.00003)
            lng += random.uniform(-0.00003, 0.00003)
            interpolated.append((lat, lng))
            
    interpolated.append(points[-1])
    return interpolated

# ----------------------------------------------------------------
# 3. 가상 데이터 생성기
# ----------------------------------------------------------------
def generate_mock_run(run_id, points, avg_speed_kmh, interval_sec, start_time_str):
    print(f"Generating mock data for run: {run_id}...")
    
    # 1. 속도와 인터벌을 통한 데이터 포인트 수 계산
    # 주행 시간 계산: 예시 거리(points 수와 위경도로 대략 산정)
    # 여기서는 보간을 통해 목표 개수를 지정해줍니다.
    # 30km 코스는 약 180포인트 (10초 간격 시 30분)
    # 200km 코스는 약 720포인트 (10초 간격 시 2시간)
    if "30km" in run_id:
        target_count = 180
    else:
        target_count = 720
        
    coords = interpolate_points(points, target_count)
    data_list = []
    
    start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    
    # 물리값 누적 시뮬레이션을 위한 초기 세팅
    current_temp = 4.2  # 기준 온도
    current_humi = 58.0  # 기준 습도
    door_open_timer = 0
    
    for idx, (lat, lng) in enumerate(coords):
        t = idx * interval_sec
        timestamp = start_dt + timedelta(seconds=t)
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # --- A. 속도 시뮬레이션 ---
        # 출발과 도착 시 감속, 주행 중 가감속 요동
        if idx < 10:  # 출발 단계
            speed = float(idx * (avg_speed_kmh / 10))
        elif idx > len(coords) - 10:  # 도착 단계
            speed = float((len(coords) - 1 - idx) * (avg_speed_kmh / 10))
        else:
            # 주행 중 속도 요동 (Gimje-Jeonju 국도는 70~85km, 고속도로는 90~110km)
            speed = avg_speed_kmh + random.uniform(-8.0, 8.0)
            
            # 중간에 일시정지 (신호 대기나 톨게이트)
            if "30km" in run_id and (60 <= idx <= 65 or 120 <= idx <= 125):
                speed = 0.0
            elif "200km" in run_id and (250 <= idx <= 265 or 500 <= idx <= 515):  # 톨게이트/휴게소 서행 및 정차
                speed = random.uniform(0.0, 15.0)

        # --- B. 온도 & 습도 시뮬레이션 ---
        # 냉동장치 가동 오실레이션 (약 10분 주기 = 60포인트 주기)
        temp_cycle = 0.8 * math.sin(2 * math.pi * idx / 60)
        humi_cycle = -2.5 * math.sin(2 * math.pi * idx / 60)
        
        # 특정 구간 도어 오픈 이벤트 (온도 튐)
        # 30km: 인덱스 90~105 부근 정차 및 하차 검수
        # 200km: 인덱스 350~390 부근 휴게소 휴식
        is_door_open = False
        if "30km" in run_id and (90 <= idx <= 105):
            is_door_open = True
        elif "200km" in run_id and (350 <= idx <= 390):
            is_door_open = True
            
        if is_door_open:
            door_open_timer += 1
            # 온도가 서서히 상승 (최대 +3.5도)
            temp_offset = min(3.5, door_open_timer * 0.25)
            humi_offset = max(-10.0, -door_open_timer * 0.7)
        else:
            if door_open_timer > 0:
                door_open_timer = max(0, door_open_timer - 1.5)  # 다시 정상 온도로 복귀
                temp_offset = door_open_timer * 0.25
                humi_offset = -door_open_timer * 0.7
            else:
                temp_offset = 0.0
                humi_offset = 0.0
                
        # 미세 노이즈 추가
        temp_noise = random.uniform(-0.15, 0.15)
        humi_noise = random.uniform(-0.5, 0.5)
        
        temperature = float(current_temp + temp_cycle + temp_offset + temp_noise)
        humidity = float(current_humi + humi_cycle + humi_offset + humi_noise)
        
        # 안전 바운더리
        temperature = max(1.5, min(12.0, temperature))
        humidity = max(35.0, min(85.0, humidity))

        # --- C. 조도 시뮬레이션 ---
        # 기본 밝기 (낮 시간 350 ~ 450 lx)
        lux_noise = random.uniform(-15.0, 15.0)
        lux = 400.0 + lux_noise
        
        # 터널 통과 시 조도 급락 이벤트
        # 30km: 인덱스 45~55 (터널)
        # 200km: 인덱스 180~195, 430~445, 600~615 (터널)
        is_in_tunnel = False
        if "30km" in run_id and (45 <= idx <= 55):
            is_in_tunnel = True
        elif "200km" in run_id and (180 <= idx <= 195 or 430 <= idx <= 445 or 600 <= idx <= 615):
            is_in_tunnel = True
            
        if is_in_tunnel:
            lux = random.uniform(3.0, 12.0)  # 터널 안은 아주 어두움

        # --- D. 충격량(G-Force) 시뮬레이션 ---
        # 기본 노면 미세 진동 (0.94G ~ 1.06G)
        g_force = 1.0 + random.uniform(-0.06, 0.06)
        
        # 간헐적 요철 충격 (1.2G ~ 1.5G) - 10% 확률로 발생
        if random.random() < 0.08 and speed > 30:
            g_force = random.uniform(1.2, 1.5)
            
        # 강한 충격 (1.8G 초과) - 특정 인덱스에서 1회씩 강제로 발생
        # 30km: 인덱스 115
        # 200km: 인덱스 220, 580
        if "30km" in run_id and idx == 115:
            g_force = 1.98
        elif "200km" in run_id and idx in [220, 580]:
            g_force = 2.14 if idx == 220 else 1.87

        # --- E. 상태(Status) 텍스트 지정 ---
        status = "Normal"
        if g_force > 1.8:
            status = "🚨 Hard Impact"
        elif is_door_open and temp_offset > 1.5:
            status = "🌡️ Sudden Temp Change"
        elif is_in_tunnel:
            status = "💡 Sudden Light Change"
            
        data_list.append({
            "device": "truck01",
            "timestamp_str": timestamp_str,
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 1),
            "lux": round(lux, 0),
            "g_force": round(g_force, 2),
            "speed": round(speed, 1),
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "status": status,
            "run_id": run_id
        })
        
    return data_list

# ----------------------------------------------------------------
# 4. 데이터베이스 주입 (Insert)
# ----------------------------------------------------------------
def insert_data_to_db(data_list):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 먼저 동일한 run_id의 기존 데이터가 있다면 중복 방지를 위해 삭제
            if data_list:
                run_id = data_list[0]["run_id"]
                cursor.execute("DELETE FROM sensor_data WHERE run_id = %s", (run_id,))
                print(f"Cleared existing data for run_id '{run_id}' from DB.")
            
            sql = """
            INSERT INTO sensor_data 
            (device, timestamp_str, temperature, humidity, lux, g_force, speed, lat, lng, status, run_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            # 벌크 인서트 진행
            vals = [
                (
                    item["device"],
                    item["timestamp_str"],
                    item["temperature"],
                    item["humidity"],
                    item["lux"],
                    item["g_force"],
                    item["speed"],
                    item["lat"],
                    item["lng"],
                    item["status"],
                    item["run_id"]
                ) for item in data_list
            ]
            cursor.executemany(sql, vals)
        conn.commit()
        print(f"Successfully inserted {len(data_list)} rows into DB.")
    except Exception as e:
        print(f"Database insert failed: {e}")
        conn.rollback()
    finally:
        conn.close()

# ----------------------------------------------------------------
# 5. 실행 제어 및 메인 함수
# ----------------------------------------------------------------
if __name__ == "__main__":
    # --- 코스 A: 김제시청 ~ 전주시청 (30km 테스트 코스) ---
    gimje_jeonju_nodes = [
        (35.800500, 126.880800),  # 김제시청 (출발)
        (35.821000, 126.915000),  # 21번 국도 합류 지점
        (35.845000, 126.960000),  # 백구 교차로 부근
        (35.865000, 127.050000),  # 삼례/조촌 교차로 부근
        (35.860000, 127.085000),  # 전주IC/여의동 부근
        (35.845000, 127.125000),  # 전주 덕진광장 교차로
        (35.824200, 127.148000),  # 전주시청 (도착)
    ]
    
    # --- 코스 B: 전주시청 ~ 서울시청 (200km 테스트 코스) ---
    jeonju_seoul_nodes = [
        (35.824200, 127.148000),  # 전주시청 (출발)
        (35.875000, 127.065000),  # 전주IC 진입 (호남고속도로)
        (35.980000, 127.080000),  # 익산JC
        (36.140000, 127.090000),  # 논산JC (천안논산고속도로 진입)
        (36.310000, 127.110000),  # 탄천휴게소 부근
        (36.430000, 127.160000),  # 공주JC
        (36.560000, 127.190000),  # 정안휴게소 부근
        (36.780000, 127.180000),  # 천안JC (경부고속도로 진입)
        (36.980000, 127.100000),  # 안성IC 부근
        (37.150000, 127.080000),  # 오산IC 부근
        (37.330000, 127.100000),  # 신갈JC 부근
        (37.460000, 127.040000),  # 양재IC 진입
        (37.520000, 127.015000),  # 한남대교 남단
        (37.566500, 126.978000),  # 서울시청 (도착)
    ]
    
    # 김제-전주 30km 가상 주행 데이터 생성 및 적재
    gimje_run_data = generate_mock_run(
        run_id="korea_30km_test",
        points=gimje_jeonju_nodes,
        avg_speed_kmh=75.0,
        interval_sec=10,
        start_time_str="2026-07-15 09:00:00"
    )
    insert_data_to_db(gimje_run_data)
    
    print("-" * 50)
    
    # 전주-서울 200km 가상 주행 데이터 생성 및 적재
    seoul_run_data = generate_mock_run(
        run_id="korea_200km_test",
        points=jeonju_seoul_nodes,
        avg_speed_kmh=100.0,
        interval_sec=10,
        start_time_str="2026-07-15 13:00:00"
    )
    insert_data_to_db(seoul_run_data)
    
    print("Mock data generation successfully completed!")
