import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime, timezone, timedelta
import toml
import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)

print("=== [테스트] EC2 클라우드 데몬 실시간 자동 수신 검증 ===")

# 1. 테스트 패킷 생성 (2호차 가상 주행 패킷)
test_payload = {
    "device": "carrier-c6-02",
    "timestamp_str": now_kst.strftime("%Y-%m-%d %H:%M:%S"),
    "temperature": 23.5,
    "humidity": 50.2,
    "lux": 150.0,
    "g_force": 2.1,  # 1.8G 이상 충격
    "lat": 35.845000,
    "lng": 127.135000,
    "speed": 35.0,   # 주행 중
    "sats": 12,
    "status": "충격 [GPS 12]"
}

# 2. HiveMQ 브로커로 발행
broker = "broker.hivemq.com"
topic = "coldchain/truck02/sensor"

print(f"1) HiveMQ '{topic}' 토픽으로 테스트 패킷 전송 중...")
try:
    from paho.mqtt.client import CallbackAPIVersion
    client = mqtt.Client(CallbackAPIVersion.VERSION1, transport="tcp")
except Exception:
    client = mqtt.Client(transport="tcp")

client.connect(broker, 1883, 60)
client.publish(topic, json.dumps(test_payload))
client.disconnect()
print("   -> 발행 완료!")

# 3. 2초 대기 후 MySQL RDS에서 자동 적재 여부 확인
print("2) EC2 데몬이 MySQL DB에 자동 적재했는지 확인 대기 (3초)...")
time.sleep(3)

sec = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')['MySQL']
conn = pymysql.connect(
    host=sec['MYSQL_HOST'], port=sec.get('MYSQL_PORT', 3306),
    user=sec['MYSQL_USER'], password=sec['MYSQL_PASSWORD'], database=sec['MYSQL_DATABASE'],
    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cur:
    cur.execute("""
        SELECT id, device, run_id, timestamp_str, speed, g_force, status, created_at 
        FROM sensor_data 
        WHERE device = 'carrier-c6-02' 
        ORDER BY id DESC LIMIT 1
    """)
    latest = cur.fetchone()
    print("\n3) MySQL DB 최신 레코드 조회 결과:")
    print(latest)
    if latest and latest['timestamp_str'] == test_payload['timestamp_str']:
        print("\n🎉 [성공!] EC2 클라우드 데몬이 패킷을 1초 만에 자동 감지하여 DB에 정상 저장했습니다!")
    else:
        print("\n⏳ 아직 적재되지 않았거나 EC2 데몬이 가동 중인지 확인 필요.")

conn.close()
