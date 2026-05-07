import streamlit as st
from pathlib import Path

st.set_page_config(page_title="QR 스캔 횟수", layout="centered")

# Session state to store scan count
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0

st.title("📊 QR 스캔 횟수 측정")

st.markdown(f"""
### 현재 스캔 횟수: 
# {st.session_state.scan_count}
""")

if st.button("QR 스캔 (시뮬레이션)", type="primary"):
    st.session_state.scan_count += 1
    st.success("QR 코드가 성공적으로 스캔되었습니다!")
    st.balloons()

if st.button("초기화"):
    st.session_state.scan_count = 0
    st.rerun()

st.divider()

# 이미지 표시 (static 폴더에 복사된 이미지들)
st.subheader("관련 이미지")
static_dir = Path("static")
if static_dir.exists():
    images = list(static_dir.glob("*.png")) + list(static_dir.glob("*.JPG"))
    if images:
        for img in images:
            st.image(str(img), caption=img.name, use_container_width=True)
    else:
        st.write("표시할 이미지가 없습니다.")
else:
    st.write("이미지 폴더를 찾을 수 없습니다.")
