import altair as alt
import pandas as pd
import numpy as np

# 가상 데이터 생성
np.random.seed(42)
dates = pd.date_range("2026-10-02 08:00:00", periods=50, freq="5s")
speeds = np.random.uniform(20, 100, 50)
g_forces = 1.0 + np.random.exponential(0.3, 50)
g_forces[10] = 3.5 # 방지턱
g_forces[30] = 2.4 # 요철

df = pd.DataFrame({
    'timestamp': dates,
    'speed': speeds,
    'g_force': g_forces
})

# 1. 속도 레이어 (오른쪽 축)
speed_layer = alt.Chart(df).mark_line(
    color='#2ECC71', strokeWidth=1.5, opacity=0.65
).encode(
    x=alt.X('timestamp:T', axis=alt.Axis(labels=False, ticks=False), title=None),
    y=alt.Y('speed:Q', axis=alt.Axis(title='차량 속도 (km/h)', titleColor='#2ECC71', grid=False), scale=alt.Scale(zero=True))
)

# 2. 충격량 라인 레이어 (왼쪽 축)
gforce_line = alt.Chart(df).mark_line(
    color='#E74C3C', strokeWidth=2.5
).encode(
    x=alt.X('timestamp:T', axis=alt.Axis(labels=False, ticks=False), title=None),
    y=alt.Y('g_force:Q', axis=alt.Axis(title='충격량 (G-Force)', titleColor='#E74C3C', grid=True), scale=alt.Scale(zero=False))
)

# 2-1. 2.0G 이상 위험 충격 포인트 강조 (빨간 점)
shock_points = alt.Chart(df[df['g_force'] >= 2.0]).mark_circle(
    size=70, color='#E74C3C'
).encode(
    x=alt.X('timestamp:T'),
    y=alt.Y('g_force:Q'),
    tooltip=[
        alt.Tooltip('timestamp:T', title='시간'),
        alt.Tooltip('g_force:Q', title='충격량(G)', format='.2f'),
        alt.Tooltip('speed:Q', title='당시속도(km/h)', format='.1f')
    ]
)

# 2-2. 과일 손상 위험 기준선 (2.0G 주의선, 3.0G 위험선)
thresh_df = pd.DataFrame([
    {'level': 2.0, 'label': '2.0G 주의 (요철)'},
    {'level': 3.0, 'label': '3.0G 위험 (압상)'}
])

rules = alt.Chart(thresh_df).mark_rule(
    strokeDash=[4, 4], strokeWidth=1.5, opacity=0.8
).encode(
    y=alt.Y('level:Q'),
    color=alt.Color('label:N', scale=alt.Scale(domain=['2.0G 주의 (요철)', '3.0G 위험 (압상)'], range=['#FFA500', '#FF0000']), legend=alt.Legend(orient='bottom', title=None))
)

# 충격량 메인 그룹 (왼쪽 축)
gforce_group = alt.layer(gforce_line, shock_points, rules)

# 결합 (독립 Y축)
final_chart = alt.layer(speed_layer, gforce_group).resolve_scale(
    y='independent'
).properties(
    height=400
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_legend(
    labelFontSize=12,
    titleFontSize=14
)

# JSON 변환 검증
chart_dict = final_chart.to_dict()
print("✅ Altair Dual Y-Axis Chart Spec Built Successfully!")
print(f"Chart layers count: {len(chart_dict['layer'])}")
