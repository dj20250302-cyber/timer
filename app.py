import math
import time
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 반응형 CSS 스타일
# ==========================================
st.set_page_config(
    page_title="⏱️ 나만의 반응형 타이머",
    page_icon="🍳",
    layout="centered"
)

# 음식 타이머에 어울리는 따뜻하고 밝은 요리 테마 CSS
CUSTOM_CSS = """
<style>
    /* 기본 배경색: 따뜻한 크림/연노랑 */
    .stApp {
        background-color: #fffbeb;
    }

    /* 메인 카드 레이아웃 (중앙 배치) */
    .main-card {
        background-color: #ffffff;
        padding: 2.5rem 2rem;
        border-radius: 24px;
        box-shadow: 0 10px 25px rgba(217, 119, 6, 0.1);
        border: 2px solid #fde68a;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }

    /* 반응형 타이머 시간 표시 (CSS clamp 사용으로 자동 크기 조절) */
    .timer-display {
        font-family: 'Courier New', Courier, monospace;
        font-weight: 800;
        font-size: clamp(3.2rem, 13vw, 6rem);
        color: #d97706; /* 오렌지 브라운 */
        margin: 0.5rem 0 1.5rem 0;
        line-height: 1;
        letter-spacing: -2px;
    }

    /* Streamlit 진행률 바 색상 커스텀 */
    .stProgress > div > div > div > div {
        background-color: #f59e0b !important;
    }

    /* 모바일 기기에서의 버튼 정렬 개선 */
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
# 타이머의 동작 상태와 설정값을 세션 상태로 기억합니다.
if "timer_state" not in st.session_state:
    st.session_state.timer_state = "stopped"  # stopped, running, paused, finished
if "total_seconds" not in st.session_state:
    st.session_state.total_seconds = 0       # 전체 지정된 초
if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = 0   # 남은 초
if "end_time" not in st.session_state:
    st.session_state.end_time = 0.0           # 종료 절대 시간 (time.monotonic 기준)
if "input_min" not in st.session_state:
    st.session_state.input_min = 3           # 기본값: 컵라면 3분
if "input_sec" not in st.session_state:
    st.session_state.input_sec = 0


# ==========================================
# 3. 타이머 동작 제어 함수들 (콜백)
# ==========================================
def set_recipe_preset(minutes, seconds=0):
    """추천 음식 버튼을 눌렀을 때 분/초를 설정하는 함수"""
    if st.session_state.timer_state in ["stopped", "finished"]:
        st.session_state.input_min = minutes
        st.session_state.input_sec = seconds

def start_timer():
    """타이머 시작 및 일시정지 후 계속 진행 함수"""
    current_now = time.monotonic()
    
    if st.session_state.timer_state in ["stopped", "finished"]:
        # 총 시간(초) 계산
        calculated_total = (st.session_state.input_min * 60) + st.session_state.input_sec
        
        # 오류 검증: 0초일 때 실행 방지
        if calculated_total <= 0:
            st.warning("⚠️ 0분 0초 이상으로 시간을 설정해 주세요!")
            return
            
        st.session_state.total_seconds = calculated_total
        st.session_state.remaining_seconds = calculated_total
        # 정확한 종료 절대 시각 계산 (time.monotonic)
        st.session_state.end_time = current_now + calculated_total
        st.session_state.timer_state = "running"
        
    elif st.session_state.timer_state == "paused":
        # 일시정지 후 계속 시작할 경우, 남아있는 초를 기반으로 종료 시각 재계산
        st.session_state.end_time = current_now + st.session_state.remaining_seconds
        st.session_state.timer_state = "running"

def pause_timer():
    """타이머 일시정지 함수"""
    if st.session_state.timer_state == "running":
        current_now = time.monotonic()
        # 오차 없는 남아있는 시간을 계산하여 저장
        st.session_state.remaining_seconds = max(0, math.ceil(st.session_state.end_time - current_now))
        st.session_state.timer_state = "paused"

def reset_timer():
    """타이머 초기화 함수"""
    st.session_state.timer_state = "stopped"
    st.session_state.total_seconds = 0
    st.session_state.remaining_seconds = 0
    st.session_state.end_time = 0.0


# ==========================================
# 4. st.fragment 기반 실시간 화면 업데이트
# ==========================================
@st.fragment(run_every=0.5)
def render_timer_ui():
    """0.5초마다 시간 오차 없이 남아있는 시간을 계산하고 화면을 그려주는 영역"""
    
    # 1) 시간 차이 계산 (time.monotonic 기반)
    if st.session_state.timer_state == "running":
        current_now = time.monotonic()
        time_left = st.session_state.end_time - current_now
        
        if time_left <= 0:
            st.session_state.remaining_seconds = 0
            st.session_state.timer_state = "finished"
            st.rerun()  # 전체 UI 상태 업데이트
        else:
            st.session_state.remaining_seconds = math.ceil(time_left)

    # 2) MM:SS 단위 포맷팅
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

    # 4) 카드 형태 UI 출력
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="timer-display">{disp_min:02d}:{disp_sec:02d}</div>', unsafe_allow_html=True)
    st.progress(progress)
    
    # 완료 및 안내 메시지 처리
    if st.session_state.timer_state == "finished":
        st.balloons()  # 성공 풍선 효과
        st.success("🎉 시간이 다 되었습니다! 맛있는 요리가 완성되었어요! 🍽️")
    elif st.session_state.timer_state == "paused":
        st.info("⏸️ 타이머가 일시정지 상태입니다.")
    elif st.session_state.timer_state == "running":
        st.caption("🔥 요리 타이머가 작동 중입니다...")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 5. 메인 앱 화면 레이아웃
# ==========================================
st.title("⏱️ 나만의 반응형 타이머")
st.subheader("🍳 맛있는 추천 음식 조리 타이머")
st.write("원하는 추천 음식을 선택하거나 직접 분/초를 입력하고 시작을 눌러주세요.")

# --- 추천 음식 빠른 설정 버튼 ---
st.write("##### 🍽️ 추천 음식 시간 설정")
p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns(5)

# 작동 중에는 버튼 클릭 불가 처리
is_disabled = st.session_state.timer_state in ["running", "paused"]

with p_col1:
    st.button("🍜 컵라면\n(3분)", on_click=set_recipe_preset, args=(3, 0), disabled=is_disabled, use_container_width=True)
with p_col2:
    st.button("🍲 봉지라면\n(4분)", on_click=set_recipe_preset, args=(4, 0), disabled=is_disabled, use_container_width=True)
with p_col3:
    st.button("🥚 반숙계란\n(7분)", on_click=set_recipe_preset, args=(7, 0), disabled=is_disabled, use_container_width=True)
with p_col4:
    st.button("🥚 완숙계란\n(12분)", on_click=set_recipe_preset, args=(12, 0), disabled=is_disabled, use_container_width=True)
with p_col5:
    st.button("🍝 파스타\n(8분)", on_click=set_recipe_preset, args=(8, 0), disabled=is_disabled, use_container_width=True)

st.divider()

# --- 분 / 초 입력 영역 ---
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

# --- 실시간 타이머 영역 출력 ---
render_timer_ui()

st.write("")

# --- 시작 / 일시정지 / 계속 / 초기화 제어 버튼 ---
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.session_state.timer_state in ["stopped", "finished"]:
        st.button("▶️ 조리 시작", on_click=start_timer, type="primary", use_container_width=True)
    elif st.session_state.timer_state == "running":
        st.button("⏸️ 일시정지", on_click=pause_timer, type="secondary", use_container_width=True)
    elif st.session_state.timer_state == "paused":
        st.button("▶️ 계속 진행", on_click=start_timer, type="primary", use_container_width=True)

with btn_col2:
    st.button("🔄 초기화", on_click=reset_timer, use_container_width=True)
