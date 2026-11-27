#!/usr/bin/env python3
"""
Real-Time Climatic Chamber Calibration Live Graph Dashboard
Reads AWS RDS `lab225_v2.chamber_calibration_logs` every 5 seconds and renders
interactive Temperature (°C) & Relative Humidity (%RH) charts per CarrierBoard.

Run:
  python scripts/chamber_calibration/live_chamber_dashboard.py
  -> Open http://127.0.0.1:8505 in your browser
"""

import io
import csv
import os
import webbrowser
import threading
import time
from datetime import datetime, timedelta, timezone

import pymysql
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

MYSQL_HOST = os.environ.get("MYSQL_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "12345678")
MYSQL_V2_DATABASE = os.environ.get("MYSQL_V2_DATABASE", "lab225_v2")
CHAMBER_TABLE = "chamber_calibration_logs"
KST = timezone(timedelta(hours=9))

app = FastAPI(title="FDT Chamber Calibration Live Monitor")


def get_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_V2_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=8,
    )


@app.get("/api/data")
def api_data(hours: int = Query(default=24, ge=1, le=168)):
    cutoff_utc = (datetime.utcnow() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, device_id, timestamp_kst, temperature, humidity, lux, rssi, uptime_ms
                FROM `{MYSQL_V2_DATABASE}`.`{CHAMBER_TABLE}`
                WHERE created_at >= %s
                ORDER BY timestamp_kst ASC, id ASC
                """,
                (cutoff_utc,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    series: dict[str, dict] = {}
    for r in rows:
        dev = r["device_id"]
        if dev not in series:
            series[dev] = {"t": [], "temp": [], "rh": [], "rssi": [], "latest": None}
        s = series[dev]
        s["t"].append(r["timestamp_kst"])
        s["temp"].append(round(float(r["temperature"]), 3))
        s["rh"].append(round(float(r["humidity"]), 3))
        s["rssi"].append(int(r["rssi"] if r["rssi"] is not None else -127))
        s["latest"] = {
            "timestamp_kst": r["timestamp_kst"],
            "temperature": round(float(r["temperature"]), 3),
            "humidity": round(float(r["humidity"]), 3),
            "rssi": int(r["rssi"] if r["rssi"] is not None else -127),
            "count": len(s["t"]),
        }

    return JSONResponse(
        {
            "server_kst": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"),
            "hours": hours,
            "total_rows": len(rows),
            "series": series,
        }
    )


@app.get("/api/export.csv")
def api_export(hours: int = Query(default=24, ge=1, le=168)):
    cutoff_utc = (datetime.utcnow() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, session_date, device_id, mac, timestamp_kst, epoch_s, uptime_ms,
                       temperature, humidity, lux, g_force, rssi
                FROM `{MYSQL_V2_DATABASE}`.`{CHAMBER_TABLE}`
                WHERE created_at >= %s
                ORDER BY id ASC
                """,
                (cutoff_utc,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    buf = io.StringIO()
    cols = [
        "id", "session_date", "device_id", "mac", "timestamp_kst", "epoch_s",
        "uptime_ms", "temperature", "humidity", "lux", "g_force", "rssi",
    ]
    w = csv.DictWriter(buf, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)
    buf.seek(0)
    fname = f"chamber_rds_export_{datetime.now(KST).strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


HTML_PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<title>FDT 항온항습 챔버 교정 실시간 모니터링</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  body { font-family: 'Segoe UI', 'Malgun Gothic', sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }
  header { background: #1e293b; padding: 14px 24px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; border-bottom: 1px solid #334155; }
  h1 { margin: 0; font-size: 1.2rem; color: #38bdf8; }
  .controls { display: flex; gap: 10px; align-items: center; font-size: 0.9rem; }
  select, button, a.btn { background: #334155; color: #f8fafc; border: 1px solid #475569; padding: 6px 12px; border-radius: 6px; cursor: pointer; text-decoration: none; font-size: 0.88rem; }
  button:hover, a.btn:hover { background: #475569; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; padding: 16px 24px 4px 24px; }
  .card { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 14px 16px; }
  .card h3 { margin: 0 0 8px 0; font-size: 1rem; display: flex; justify-content: space-between; }
  .metric { font-size: 1.45rem; font-weight: 700; margin: 4px 0; }
  .sub { font-size: 0.82rem; color: #94a3b8; }
  .charts { display: grid; grid-template-columns: 1fr; gap: 16px; padding: 14px 24px 28px 24px; }
  .chart-box { background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 10px; min-height: 360px; }
  .badge { font-size: 0.78rem; padding: 2px 8px; border-radius: 999px; background: #0ea5e9; color: #0f172a; font-weight: 700; }
</style>
</head>
<body>
<header>
  <h1>FDT 항온항습 챔버 교정 실시간 모니터링 (AWS RDS)</h1>
  <div class="controls">
    <span id="statusTxt" class="sub">불러오는 중...</span>
    <select id="hoursSel" onchange="fetchAndRender()">
      <option value="1">최근 1시간</option>
      <option value="6">최근 6시간</option>
      <option value="24" selected>최근 24시간</option>
      <option value="48">최근 48시간</option>
    </select>
    <button onclick="fetchAndRender()">지금 새로고침</button>
    <a id="exportBtn" class="btn" href="/api/export.csv?hours=24">CSV 다운로드</a>
  </div>
</header>

<div id="cards" class="cards"></div>

<div class="charts">
  <div id="tempChart" class="chart-box"></div>
  <div id="rhChart" class="chart-box"></div>
</div>

<script>
const COLORS = {
  'carrier-c6-01': '#f59e0b',
  'carrier-c6-02': '#38bdf8',
  'carrier-c6-03': '#22c55e',
  'carrier-c6-04': '#f43f5e'
};

async function fetchAndRender() {
  const hrs = document.getElementById('hoursSel').value;
  document.getElementById('exportBtn').href = `/api/export.csv?hours=${hrs}`;
  try {
    const res = await fetch(`/api/data?hours=${hrs}`);
    const data = await res.json();
    document.getElementById('statusTxt').textContent =
      `갱신: ${data.server_kst} | 누적 ${data.total_rows.toLocaleString()}건 (5초 자동갱신)`;

    const devs = Object.keys(data.series).sort();
    const cardsEl = document.getElementById('cards');
    if (devs.length === 0) {
      cardsEl.innerHTML = '<div class="card"><h3>수신 데이터 대기 중</h3><div class="sub">선택 구간 내 chamber_calibration_logs 데이터가 없습니다.</div></div>';
    } else {
      cardsEl.innerHTML = devs.map(d => {
        const l = data.series[d].latest;
        const c = COLORS[d] || '#a78bfa';
        return `
          <div class="card" style="border-top: 3px solid ${c};">
            <h3><span>${d}</span><span class="badge" style="background:${c};">${l.count.toLocaleString()}건</span></h3>
            <div class="metric">${l.temperature.toFixed(2)} °C &nbsp;/&nbsp; ${l.humidity.toFixed(2)} %RH</div>
            <div class="sub">최신 시각: ${l.timestamp_kst} | RSSI: ${l.rssi} dBm</div>
          </div>`;
      }).join('');
    }

    const tempTraces = devs.map(d => ({
      x: data.series[d].t,
      y: data.series[d].temp,
      mode: 'lines',
      name: d,
      line: { width: 2.2, color: COLORS[d] || '#a78bfa' }
    }));
    const rhTraces = devs.map(d => ({
      x: data.series[d].t,
      y: data.series[d].rh,
      mode: 'lines',
      name: d,
      line: { width: 2.2, color: COLORS[d] || '#a78bfa' }
    }));

    const baseLayout = (title, ytitle) => ({
      title: { text: title, font: { color: '#f8fafc', size: 15 } },
      paper_bgcolor: '#1e293b',
      plot_bgcolor: '#0f172a',
      font: { color: '#cbd5e1' },
      margin: { t: 44, r: 24, b: 44, l: 58 },
      xaxis: { title: '시각 (KST)', gridcolor: '#1e293b' },
      yaxis: { title: ytitle, gridcolor: '#334155' },
      legend: { orientation: 'h', y: 1.12 },
      hovermode: 'x unified'
    });

    Plotly.react('tempChart', tempTraces, baseLayout('실시간 온도 추이 (°C)', 'Temperature (°C)'), { responsive: true });
    Plotly.react('rhChart', rhTraces, baseLayout('실시간 상대습도 추이 (%RH)', 'Humidity (%RH)'), { responsive: true });
  } catch (err) {
    document.getElementById('statusTxt').textContent = '조회 오류: ' + err;
  }
}

fetchAndRender();
setInterval(fetchAndRender, 5000);
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return HTML_PAGE


def main():
    port = int(os.environ.get("CHAMBER_DASH_PORT", "8505"))
    url = f"http://127.0.0.1:{port}"
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    print(f"[START] 챔버 실시간 그래프 대시보드 실행 중 -> {url}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
