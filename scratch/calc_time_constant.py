import pymysql
import math
import datetime

conn = pymysql.connect(
    host="labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com",
    port=3306,
    user="admin",
    password="12345678",
    database="lab225",
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cursor:
    cursor.execute("""
        SELECT timestamp_str, temperature, lux
        FROM sensor_data
        WHERE created_at >= '2026-10-06 12:47:00' AND created_at <= '2026-10-06 13:36:00'
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
conn.close()

if not rows:
    print("No rows found")
    exit()

times = []
temps = []
t0 = datetime.datetime.strptime(rows[0]['timestamp_str'], "%Y-%m-%d %H:%M:%S")

for r in rows:
    ts = datetime.datetime.strptime(r['timestamp_str'], "%Y-%m-%d %H:%M:%S")
    t_sec = (ts - t0).total_seconds()
    times.append(t_sec)
    temps.append(float(r['temperature']))

T_0 = temps[0] # 27.62
T_inf = 4.5    # 가정: 냉장고 최저 수렴 온도 약 4.5°C

# 선형 회귀: y = -t / tau => y = ln((T - T_inf) / (T_0 - T_inf))
valid_t = []
y_vals = []
for t, T in zip(times, temps):
    if T > T_inf + 0.2:
        ratio = (T - T_inf) / (T_0 - T_inf)
        if ratio > 0:
            valid_t.append(t)
            y_vals.append(math.log(ratio))

# 최소자승법 (y = m * x)
n = len(valid_t)
mean_x = sum(valid_t) / n
mean_y = sum(y_vals) / n
slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(valid_t, y_vals)) / sum((x - mean_x)**2 for x in valid_t)

tau = -1.0 / slope

print(f"Data points: {len(temps)}")
print(f"Initial Temp T_0: {T_0:.2f} °C")
print(f"Lowest Temp:     {min(temps):.2f} °C")
print(f"Assumed Fridge T_inf: {T_inf:.1f} °C")
print(f"Estimated Time Constant (tau): {tau:.1f} sec ({tau/60:.1f} min)")

# 63.2% 도달 온도
T_63 = T_0 - 0.632 * (T_0 - T_inf)
print(f"63.2% Response Temp: {T_63:.2f} °C")

# 실제 63.2% 도달 시각 실측치 찾기
for t, T in zip(times, temps):
    if T <= T_63:
        print(f"Actual measured time to reach 63.2%: {t:.0f} sec ({t/60:.1f} min)")
        break
