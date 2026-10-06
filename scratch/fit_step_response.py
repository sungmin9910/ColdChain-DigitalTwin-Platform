import pymysql
import numpy as np
from scipy.optimize import curve_fit
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
        WHERE timestamp_str BETWEEN '2026-10-06 21:47:50' AND '2026-10-06 22:35:40'
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
conn.close()

times = []
temps = []
t0 = None
for r in rows:
    ts = datetime.datetime.strptime(r['timestamp_str'], "%Y-%m-%d %H:%M:%S")
    if t0 is None:
        t0 = ts
    times.append((ts - t0).total_seconds())
    temps.append(float(r['temperature']))

times = np.array(times)
temps = np.array(temps)

# 1차 지연 냉각 모델: T(t) = T_inf + (T_0 - T_inf) * exp(-t / tau)
T_0 = temps[0]  # 27.62
def cooling_model(t, T_inf, tau):
    return T_inf + (T_0 - T_inf) * np.exp(-t / tau)

popt, pcov = curve_fit(cooling_model, times, temps, p0=[4.0, 1000.0])
T_inf_est, tau_est = popt

print(f"Initial Temp T_0: {T_0:.2f} °C")
print(f"Estimated Fridge Temp T_inf: {T_inf_est:.2f} °C")
print(f"Estimated Time Constant tau: {tau_est:.1f} seconds ({tau_est/60:.1f} minutes)")

# R-squared
residuals = temps - cooling_model(times, *popt)
ss_res = np.sum(residuals**2)
ss_tot = np.sum((temps - np.mean(temps))**2)
r_squared = 1 - (ss_res / ss_tot)
print(f"Model Fit R^2: {r_squared:.4f}")
