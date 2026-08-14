import math
import time
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 반응형 CSS 스타일
# ==========================================
st.set_page_config(
    page_title="⏱️ 나만의 파란색 타이머",
    page_icon="⏱️",
    layout="centered"
)

# 파란색 테마(Blue Theme) 및 반응형 CSS 스타일
CUSTOM_CSS = """
<style>
    /* 기본 배경 및 폰트 설정 */
    .stApp {
        background-color: #f0f7ff;
    }

    /* 메인 타이머 카드 디자인 (파란색 테마) */
    .main-card {
        background-color: #ffffff;
        padding: 2.5rem 2rem;
        border-radius: 24px;
        box-shadow: 0 12px 30px rgba(30, 58, 138, 0.08);
        border: 2px solid #dbeafe;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }

    /* 반응형 타이머 시간 표시 (파란색 메인 컬러) */
    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        font-weight: 800;
        font-size: clamp(3.2rem, 13vw, 6rem);
        color: #1e40af; /* Deep Blue */
        margin: 0.5rem 0 1.5rem 0;
        line-height: 1;
        letter-spacing: -2px;
    }

    /* Streamlit 진행률 바 색상을 파란색으로 변경 */
    .stProgress > div > div > div > div {
        background-color: #2563eb !important;
    }

    /* 반응형 버튼 트릭: 모바일 화면에서 버튼 자동 정렬 */
    @media (max-width: 600px) {
        .stButton > button {
            width: 100% !important;
            margin-bottom: 0.25rem;
        }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==========================================
# 2. 세션 상태(st.session_state) 초기화
# ==========================================
if "timer_state" not in st.session_state:
    st.session_state.timer_state = "stopped"  # 상태: stopped, running, paused, finished
if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 0
if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 0
if "end_time" not in st.session_state:
    st.session_state.end_time = 0.0
if "input_min" not in st.session_state:
    st.session_state.input_min = 1
if "input_sec" not in st.session_state:
    st.session_state.input_sec = 0


# ==========================================
# 3. 타이머 제어 함수들 (콜백 함수)
# ==========================================
def set_preset_time(minutes):
    """빠른 설정 버튼 클릭 시 적용"""
    if st.session_state.timer_state in ["stopped", "finished"]:
        st.session_state.input_min = minutes
        st.session_state.input_sec = 0

def start_timer():
    """타이머 시작 / 계속"""
    current_now = time.monotonic()
    
    if st.session_state.timer_state in ["stopped", "finished"]:
        calculated_total = (st.session_state.input_min * 60) + st.session_state.input_sec
        if calculated_total <= 0:
            st.warning("⚠️ 0분 0초 이상으로 시간을 설정해 주세요!")
            return
        st.session_state.total_seconds = calculated_total
        st.session_state.remaining_seconds = calculated_total
        st.session_state.end_time = current_now + calculated_total
        st.session_state.timer_state = "running"
        
    elif st.session_state.timer_state == "paused":
        st.session_state.end_time = current_now + st.session_state.remaining_seconds
        st.session_state.timer_state = "running"

def pause_timer():
    """타이머 일시정지"""
    if st.session_state.timer_state == "running":
        current_now = time.monotonic()
        st.session_state.remaining_seconds = max(0, math.ceil(st.session_state.end_time - current_now))
        st.session_state.timer_state = "paused"

def reset_timer():
    """타이머 초기화"""
    st.session_state.timer_state = "stopped"
    st.session_state.total_seconds = 0
    st.session_state.remaining_seconds = 0
    st.session_state.end_time = 0.0


# ==========================================
# 4. st.fragment를 활용한 실시간 타이머 영역
# ==========================================
@st.fragment(run_every=0.5)
def render_timer_ui():
    """실시간으로 남은 시간 및 진행률 바 업데이트"""
    
    # 1) 시간 업데이트 계산 (time.monotonic 기반)
    if st.session_state.timer_state == "running":
        current_now = time.monotonic()
        time_left = st.session_state.end_time - current_now
        
        if time_left <= 0:
            st.session_state.remaining_seconds = 0
            st.session_state.timer_state = "finished"
            st.rerun()
        else:
            st.session_state.remaining_seconds = math.ceil(time_left)

    # 2) 표시할 시간 계산
    rem_sec = st.session_state.remaining_seconds
    
    if st.session_state.timer_state in ["stopped", "finished"] and rem_sec == 0:
        disp_min = st.session_state.input_min
        disp_sec = st.session_state.input_sec
    else:
        disp_min = rem_sec // 60
        disp_sec = rem_sec % 60

    # 3) 진행률 계산
    if st.session_state.total_seconds > 0:
        progress = max(0.0, min(1.0, rem_sec / st.session_state.total_seconds))
    else:
        progress = 1.0

    # 4) 타이머 UI 카드 출력
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="timer-display">{disp_min:02d}:{disp_sec:02d}</div>', unsafe_allow_html=True)
    st.progress(progress)
    
    # 완료 및 안내 메시지
    if st.session_state.timer_state == "finished":
        st.balloons()
        st.success("🎉 시간이 다 되었습니다! 수고하셨습니다.")
    elif st.session_state.timer_state == "paused":
        st.info("⏸️ 타이머가 일시정지되었습니다.")
    elif st.session_state.timer_state == "running":
        st.caption("🔷 타이머가 작동 중입니다...")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 5. 메인 화면 구성
# ==========================================
st.title("⏱️ 블루 타이머")
st.write("원하는 시간을 설정하고 시작 버튼을 눌러주세요.")

# --- 빠른 시간 설정 버튼 ---
st.write("##### 🚀 빠른 시간 설정")
p_col1, p_col2, p_col3, p_col4 = st.columns(4)

is_disabled = st.session_state.timer_state in ["running", "paused"]

with p_col1:
    st.button("1분", on_click=set_preset_time, args=(1,), disabled=is_disabled, use_container_width=True)
with p_col2:
    st.button("3분", on_click=set_preset_time, args=(3,), disabled=is_disabled, use_container_width=True)
with p_col3:
    st.button("5분", on_click=set_preset_time, args=(5,), disabled=is_disabled, use_container_width=True)
with p_col4:
    st.button("10분", on_click=set_preset_time, args=(10,), disabled=is_disabled, use_container_width=True)

st.divider()

# --- 분 / 초 입력창 ---
in_col1, in_col2 = st.columns(2)
with in_col1:
    st.number_input(
        "분 (Min)",
        min_value=0,
        max_value=999,
        key="input_min",
        disabled=is_disabled
    )
with in_col2:
    st.number_input(
        "초 (Sec)",
        min_value=0,
        max_value=59,
        key="input_sec",
        disabled=is_disabled
    )

# 실시간 타이머 영역 랜더링
render_timer_ui()

st.write("")

# --- 제어 버튼 영역 ---
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.session_state.timer_state in ["stopped", "finished"]:
        st.button("▶️ 시작", on_click=start_timer, type="primary", use_container_width=True)
    elif st.session_state.timer_state == "running":
        st.button("⏸️ 일시정지", on_click=pause_timer, type="secondary", use_container_width=True)
    elif st.session_state.timer_state == "paused":
        st.button("▶️ 계속", on_click=start_timer, type="primary", use_container_width=True)

with btn_col2:
    st.button("🔄 초기화", on_click=reset_timer, use_container_width=True)
