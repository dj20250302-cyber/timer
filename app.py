import time
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 모바일 맞춤 반응형 CSS
# ==========================================
st.set_page_config(
    page_title="⏱️ 나만의 반응형 타이머",
    page_icon="⏱️",
    layout="centered"
)

# 모바일, 태블릿, PC 지원을 위한 clamp() 및 커스텀 스타일링 적용
custom_css = """
<style>
/* 카드 형태 중앙 박스 스타일 */
.timer-card {
    background-color: #ffffff;
    border-radius: 20px;
    padding: 30px 20px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
    text-align: center;
    margin-bottom: 25px;
    border: 1px solid #eef2f6;
}

/* clamp(최소크기, 권장크기, 최대크기)를 사용한 반응형 타이머 폰트 */
.timer-display {
    font-size: clamp(3rem, 12vw, 6rem);
    font-weight: 800;
    color: #2c3e50;
    font-family: 'Courier New', Courier, monospace;
    letter-spacing: 2px;
    margin: 10px 0;
}

/* 모바일 화면을 고려한 버튼 패딩 및 여백 자동 조정 */
div.stButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: 600;
    padding: 10px 16px;
    border: none;
    transition: all 0.2s ease;
}

/* 진행률 바 커스텀 */
.stProgress > div > div > div > div {
    background-color: #4ea8de;
    border-radius: 10px;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# 2. 세션 상태(st.session_state) 초기화
# ==========================================
# 앱이 새로고침되어도 타이머의 동작 상태를 안전하게 유지합니다.
if "timer_state" not in st.session_state:
    st.session_state.timer_state = "stopped"  # 상태: stopped, running, paused, finished
if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 0.0
if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 0.0
if "target_end_time" not in st.session_state:
    st.session_state.target_end_time = 0.0
if "input_minutes" not in st.session_state:
    st.session_state.input_minutes = 3
if "input_seconds" not in st.session_state:
    st.session_state.input_seconds = 0


# ==========================================
# 3. 타이머 제어 함수 정의
# ==========================================
def set_quick_time(minutes: int):
    """빠른 시간 설정 버튼 클릭 시 호출되는 함수"""
    if st.session_state.timer_state == "stopped":
        st.session_state.input_minutes = minutes
        st.session_state.input_seconds = 0

def start_timer():
    """타이머 시작 함수"""
    total = (st.session_state.input_minutes * 60) + st.session_state.input_seconds
    if total <= 0:
        st.warning("⚠️ 0분 0초 이상 시간을 설정해 주세요!")
        return
    
    st.session_state.total_seconds = float(total)
    st.session_state.remaining_seconds = float(total)
    # 실제 시스템 시각과 동기화하기 위해 time.monotonic() 기준 종료 시각 설정
    st.session_state.target_end_time = time.monotonic() + float(total)
    st.session_state.timer_state = "running"

def pause_timer():
    """타이머 일시정지 함수"""
    if st.session_state.timer_state == "running":
        # 현재 남은 시간을 정확하게 계산하여 저장
        now = time.monotonic()
        st.session_state.remaining_seconds = max(0.0, st.session_state.target_end_time - now)
        st.session_state.timer_state = "paused"

def resume_timer():
    """타이머 계속(재개) 함수"""
    if st.session_state.timer_state == "paused":
        # 남은 시간을 기준으로 새로운 종료 목표 시각 설정
        st.session_state.target_end_time = time.monotonic() + st.session_state.remaining_seconds
        st.session_state.timer_state = "running"

def reset_timer():
    """타이머 초기화 함수"""
    st.session_state.timer_state = "stopped"
    st.session_state.total_seconds = 0.0
    st.session_state.remaining_seconds = 0.0
    st.session_state.target_end_time = 0.0


# ==========================================
# 4. 앱 헤더 및 타이틀
# ==========================================
st.markdown("<h1 style='text-align: center;'>⏱️ 나만의 반응형 타이머</h1>", unsafe_allow_html=True)
st.caption("스마트폰과 PC에서 모두 깔끔하게 작동하는 초정밀 카운트다운 타이머입니다.")
st.write("")


# ==========================================
# 5. 빠른 시간 설정 버튼 (1분, 3분, 5분, 10분)
# ==========================================
is_disabled = st.session_state.timer_state in ["running", "paused"]

st.write("⚡ **빠른 시간 선택**")
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

with q_col1:
    st.button("1분", on_click=set_quick_time, args=(1,), disabled=is_disabled, use_container_width=True)
with q_col2:
    st.button("3분", on_click=set_quick_time, args=(3,), disabled=is_disabled, use_container_width=True)
with q_col3:
    st.button("5분", on_click=set_quick_time, args=(5,), disabled=is_disabled, use_container_width=True)
with q_col4:
    st.button("10분", on_click=set_quick_time, args=(10,), disabled=is_disabled, use_container_width=True)

st.write("---")


# ==========================================
# 6. 시간 직접 입력 영역
# ==========================================
col_min, col_sec = st.columns(2)

with col_min:
    st.number_input(
        "분 (Minutes)",
        min_value=0,
        max_value=999,
        key="input_minutes",
        disabled=is_disabled,
        help="0분 이상 입력 가능합니다."
    )

with col_sec:
    st.number_input(
        "초 (Seconds)",
        min_value=0,
        max_value=59,
        key="input_seconds",
        disabled=is_disabled,
        help="0초부터 59초까지 입력 가능합니다."
    )


# ==========================================
# 7. 타이머 화면 갱신 영역 (st.fragment 적용)
# ==========================================
# st.fragment를 사용해 페이지 전체를 다시 그리지 않고, 해당 영역만 매초 주기로 갱신합니다.
@st.fragment(run_every="1s" if st.session_state.timer_state == "running" else None)
def render_timer():
    state = st.session_state.timer_state

    # 1) 실행 중인 경우 남은 시간 업데이트
    if state == "running":
        now = time.monotonic()
        remaining = st.session_state.target_end_time - now
        
        if remaining <= 0:
            st.session_state.remaining_seconds = 0.0
            st.session_state.timer_state = "finished"
        else:
            st.session_state.remaining_seconds = remaining

    # 2) 표시용 분/초 계산
    curr_remaining = int(round(st.session_state.remaining_seconds))
    mins = curr_remaining // 60
    secs = curr_remaining % 60
    time_str = f"{mins:02d}:{secs:02d}"

    # 3) 타이머 중앙 시각화 디스플레이
    st.markdown(
        f"""
        <div class="timer-card">
            <div style="font-size: 0.9rem; color: #7f8c8d; font-weight: 600;">남은 시간</div>
            <div class="timer-display">{time_str}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4) 진행률 표시 (Progress Bar)
    if st.session_state.total_seconds > 0:
        progress_val = max(0.0, min(1.0, st.session_state.remaining_seconds / st.session_state.total_seconds))
    else:
        progress_val = 0.0
    st.progress(progress_val)

    # 5) 완료 상태 처리 (성공 메시지 & 풍선 효과)
    if st.session_state.timer_state == "finished":
        st.balloons()
        st.success("🎉 설정한 시간이 완료되었습니다!")


# 타이머 프래그먼트 호출
render_timer()


# ==========================================
# 8. 컨트롤 버튼 영역 (시작 / 일시정지 / 계속 / 초기화)
# ==========================================
st.write("")
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.session_state.timer_state == "stopped":
        st.button("▶️ 시작", on_click=start_timer, type="primary", use_container_width=True)
    elif st.session_state.timer_state == "running":
        st.button("⏸️ 일시정지", on_click=pause_timer, use_container_width=True)
    elif st.session_state.timer_state == "paused":
        st.button("▶️ 계속", on_click=resume_timer, type="primary", use_container_width=True)
    elif st.session_state.timer_state == "finished":
        st.button("▶️ 다시 시작", on_click=start_timer, type="primary", use_container_width=True)

with btn_col2:
    st.button("🔄 초기화", on_click=reset_timer, use_container_width=True)
