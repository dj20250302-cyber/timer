import math
import time
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 반응형 CSS 스타일
# ==========================================
st.set_page_config(
    page_title="⏱️ 나만의 반응형 타이머",
    page_icon="⏱️",
    layout="centered"
)

# 반응형 카드 레이아웃과 clamp()를 이용한 글자 크기 자동 조절 CSS
CUSTOM_CSS = """
<style>
    /* 배경 및 카드 디자인 */
    .main-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid #eef2f6;
        text-align: center;
        margin-top: 1rem;
    }

    /* 반응형 타이머 시간 표시 (clamp 활용: 최소, 권장, 최대 크기) */
    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        font-weight: 800;
        font-size: clamp(3rem, 12vw, 5.5rem);
        color: #2c3e50;
        margin: 1rem 0;
        line-height: 1;
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
# 타이머가 동작하는 동안 데이터를 기억하기 위한 변수들입니다.
if "timer_state" not in st.session_state:
    st.session_state.timer_state = "stopped"  # 상태: stopped(정지), running(실행중), paused(일시정지), finished(완료)
if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 0       # 설정된 전체 시간(초)
if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 0   # 남은 시간(초)
if "end_time" not in st.session_state:
    st.session_state.end_time = 0.0           # 타이머가 끝날 절대 시각 (time.monotonic 기준)
if "input_min" not in st.session_state:
    st.session_state.input_min = 1           # 기본 설정 분
if "input_sec" not in st.session_state:
    st.session_state.input_sec = 0           # 기본 설정 초


# ==========================================
# 3. 타이머 제어 함수들 (콜백 함수)
# ==========================================
def set_preset_time(minutes):
    """빠른 설정 버튼을 눌렀을 때 시간을 설정하는 함수"""
    if st.session_state.timer_state in ["stopped", "finished"]:
        st.session_state.input_min = minutes
        st.session_state.input_sec = 0

def start_timer():
    """타이머를 시작하거나 계속(Resume) 진행하는 함수"""
    current_now = time.monotonic()
    
    if st.session_state.timer_state in ["stopped", "finished"]:
        # 정지 상태에서 새로 시작하는 경우
        calculated_total = (st.session_state.input_min * 60) + st.session_state.input_sec
        if calculated_total <= 0:
            st.warning("⚠️ 0분 0초 이상으로 시간을 설정해 주세요!")
            return
        st.session_state.total_seconds = calculated_total
        st.session_state.remaining_seconds = calculated_total
        st.session_state.end_time = current_now + calculated_total
        st.session_state.timer_state = "running"
        
    elif st.session_state.timer_state == "paused":
        # 일시정지 상태에서 다시 시작하는 경우 (남은 시간 기반으로 종료 시각 재계산)
        st.session_state.end_time = current_now + st.session_state.remaining_seconds
        st.session_state.timer_state = "running"

def pause_timer():
    """타이머를 일시정지하는 함수"""
    if st.session_state.timer_state == "running":
        current_now = time.monotonic()
        # 정밀도를 위해 남은 시간을 올림(ceil) 계산하여 저장
        st.session_state.remaining_seconds = max(0, math.ceil(st.session_state.end_time - current_now))
        st.session_state.timer_state = "paused"

def reset_timer():
    """타이머를 처음 상태로 초기화하는 함수"""
    st.session_state.timer_state = "stopped"
    st.session_state.total_seconds = 0
    st.session_state.remaining_seconds = 0
    st.session_state.end_time = 0.0


# ==========================================
# 4. st.fragment를 활용한 주파수 기반 새로고침
# ==========================================
# run_every=0.5초마다 이 함수 영역만 독립적으로 다시 실행하여 화면을 업데이트합니다.
@st.fragment(run_every=0.5)
def render_timer_ui():
    """타이머의 남은 시간 및 진행률을 실시간으로 그려주는 프래그먼트"""
    
    # 1) 실행 중(running)일 때 시간 업데이트 계산 (time.monotonic 활용)
    if st.session_state.timer_state == "running":
        current_now = time.monotonic()
        time_left = st.session_state.end_time - current_now
        
        if time_left <= 0:
            st.session_state.remaining_seconds = 0
            st.session_state.timer_state = "finished"
            st.rerun()  # 상태가 변경되었으므로 전체 화면 갱신
        else:
            st.session_state.remaining_seconds = math.ceil(time_left)

    # 2) 화면에 보여줄 초 단위 계산
    rem_sec = st.session_state.remaining_seconds
    
    if st.session_state.timer_state in ["stopped", "finished"] and rem_sec == 0:
        # 타이머 시작 전에는 입력 박스의 시간을 미리 표시
        disp_min = st.session_state.input_min
        disp_sec = st.session_state.input_sec
    else:
        disp_min = rem_sec // 60
        disp_sec = rem_sec % 60

    # 3) 진행률 막대(Progress Bar) 계산
    if st.session_state.total_seconds > 0:
        progress = max(0.0, min(1.0, rem_sec / st.session_state.total_seconds))
    else:
        progress = 1.0

    # 4) 타이머 UI 카드 출력
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # 시각적 타이머 텍스트 (MM:SS)
    st.markdown(f'<div class="timer-display">{disp_min:02d}:{disp_sec:02d}</div>', unsafe_allow_html=True)
    
    # 진행률 표시 바
    st.progress(progress)
    
    # 완료 상태 처리 및 풍선 효과
    if st.session_state.timer_state == "finished":
        st.balloons()
        st.success("🎉 시간이 다 되었습니다! 수고하셨습니다.")
    elif st.session_state.timer_state == "paused":
        st.info("⏸️ 타이머가 일시정지되었습니다.")
    elif st.session_state.timer_state == "running":
        st.caption("⏱️ 타이머가 동작 중입니다...")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 5. 메인 앱 화면 구성
# ==========================================
st.title("⏱️ 나만의 반응형 타이머")
st.write("원하는 시간을 설정하고 시작 버튼을 눌러주세요.")

# --- 빠른 설정 버튼 (1분, 3분, 5분, 10분) ---
st.write("##### 🚀 빠른 시간 설정")
p_col1, p_col2, p_col3, p_col4 = st.columns(4)

# 실행 중이거나 일시정지 중일 때는 설정 버튼 비활성화
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

# --- 분 / 초 입력창 설정 ---
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

# --- 실시간 타이머 표시 영역 (Fragment 함수 호출) ---
render_timer_ui()

st.write("")

# --- 제어 버튼 영역 (시작/일시정지/계속/초기화) ---
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
