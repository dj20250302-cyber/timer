import random
import streamlit as st

# ==========================================
# 1. 페이지 기본 설정 및 반응형 CSS 스타일
# ==========================================
st.set_page_config(
    page_title="🍽️ 오늘 뭐 먹지? 무작위 요리 추천기",
    page_icon="🍳",
    layout="centered"
)

# 음식 추천 앱에 어울리는 따뜻한 오렌지/크림 테마 CSS
CUSTOM_CSS = """
<style>
    /* 전체 배경색: 따뜻하고 밝은 크림 톤 */
    .stApp {
        background-color: #fffbf0;
    }

    /* 메인 결과 카드 레이아웃 */
    .result-card {
        background-color: #ffffff;
        padding: 2.5rem 2rem;
        border-radius: 24px;
        box-shadow: 0 12px 30px rgba(217, 119, 6, 0.12);
        border: 2px solid #fde68a;
        text-align: center;
        margin: 1.5rem 0;
    }

    /* 추천 메뉴 이름 텍스트 (CSS clamp로 반응형 크기 조절) */
    .dish-title {
        font-weight: 800;
        font-size: clamp(2.2rem, 8vw, 3.8rem);
        color: #d97706; /* 따뜻한 오렌지 브라운 */
        margin: 0.5rem 0;
        line-height: 1.2;
    }

    /* 카테고리 태그 및 설명 텍스트 */
    .dish-category {
        display: inline-block;
        background-color: #fef3c7;
        color: #b45309;
        font-weight: 700;
        padding: 0.4rem 1.2rem;
        border-radius: 20px;
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
    }

    /* 모바일 버튼 반응형 스타일 */
    @media (max-width: 600px) {
        .stButton > button {
            width: 100% !important;
            margin-bottom: 0.3rem;
        }
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==========================================
# 2. 요리 메뉴 데이터베이스 (리스트 & 딕셔너리)
# ==========================================
# 초보자도 메뉴를 쉽게 추가하거나 수정할 수 있는 데이터 구조입니다.
DISHES_DATABASE = [
    {
        "name": "🍜 김치찌개",
        "category": "한식 🇰🇷",
        "desc": "매콤하고 얼큰한 국물이 생각날 때 최고의 선택!",
        "tip": "돼지고기와 푹 익은 신김치를 달달 볶아 끓여보세요."
    },
    {
        "name": "🍲 된장찌개",
        "category": "한식 🇰🇷",
        "desc": "구수하고 정갈한 한국인의 대표 집밥 요리",
        "tip": "두부와 애호박, 버섯을 듬뿍 넣으면 더 풍성해집니다."
    },
    {
        "name": "🍛 카레라이스",
        "category": "일식/양식 🇯🇵",
        "desc": "만들기 쉽고 한 그릇으로 든든한 든든한 한 끼",
        "tip": "양파를 갈색이 될 때까지 오래 볶으면 풍미가 깊어집니다."
    },
    {
        "name": "🍝 알리오 올리오 파스타",
        "category": "양식 🇮🇹",
        "desc": "마늘과 올리브 오일의 고소하고 알싸한 풍미",
        "tip": "면수와 올리브 오일을 잘 섞어 유화시키는 것이 핵심!"
    },
    {
        "name": "🥟 마라탕",
        "category": "중식 🇨🇳",
        "desc": "얼얼하고 매콤해서 스트레스가 싹 풀리는 메뉴",
        "tip": "좋아하는 버섯, 푸주, 분모자를 취향껏 넣어보세요."
    },
    {
        "name": "🍳 햄 계란볶음밥",
        "category": "간편식 ⚡",
        "desc": "냉장고 파먹기에 딱 좋은 초간단 메뉴",
        "tip": "파기름을 먼저 내고 찬밥을 눌러가며 볶아주세요."
    },
    {
        "name": "🥪 클럽 샌드위치",
        "category": "간편식 ⚡",
        "desc": "신선한 야채와 계란, 베이컨의 환상 조합",
        "tip": "식빵 안쪽에 마요네즈나 머스타드를 바르면 눅눅해지지 않아요."
    },
    {
        "name": "🌮 타코",
        "category": "세계요리 🇲🇽",
        "desc": "이색적이고 화려한 풍미를 즐기고 싶을 때",
        "tip": "라임즙과 살사 소스를 취향껏 더해보세요."
    },
    {
        "name": "🥩 찹스테이크",
        "category": "양식 🇺🇸",
        "desc": "달콤 짭조름한 소스와 두툼한 고기의 식감",
        "tip": "파프리카와 양파를 큼직하게 썰어 함께 볶아주세요."
    },
    {
        "name": "떡볶이 🌶️",
        "category": "분식 🇰🇷",
        "desc": "매콤달콤 국민 간식이자 영원한 영혼의 음식",
        "tip": "삶은 계란과 어묵, 삶은 당면을 추가하면 최고!"
    }
]


# ==========================================
# 3. 세션 상태(st.session_state) 초기화
# ==========================================
if "current_dish" not in st.session_state:
    st.session_state.current_dish = None  # 현재 추천된 요리 데이터
if "history" not in st.session_state:
    st.session_state.history = []         # 뽑았던 메뉴 기록


# ==========================================
# 4. 요리 추천 로직 함수들
# ==========================================
def recommend_random_dish(selected_category="전체"):
    """선택한 카테고리에 맞는 요리를 무작위로 추첨하는 함수"""
    if selected_category == "전체":
        candidates = DISHES_DATABASE
    else:
        candidates = [d for d in DISHES_DATABASE if selected_category in d["category"]]
    
    if candidates:
        chosen = random.choice(candidates)
        st.session_state.current_dish = chosen
        
        # 최근 추천 기록 저장 (최대 5개까지 유지)
        if chosen["name"] not in st.session_state.history:
            st.session_state.history.insert(0, chosen["name"])
            if len(st.session_state.history) > 5:
                st.session_state.history.pop()


# ==========================================
# 5. 메인 앱 화면 구성
# ==========================================
st.title("🍽️ 오늘 뭐 먹지?")
st.subheader("🎲 고민 해결! 무작위 요리 추천기")
st.write("결정 장애가 올 땐 버튼을 눌러 오늘 먹을 요리를 추천받아 보세요!")

st.divider()

# --- 카테고리 필터 선택 ---
categories = ["전체", "한식 🇰🇷", "양식 🇮🇹", "중식 🇨🇳", "간편식 ⚡", "분식 🇰🇷"]
selected_cat = st.selectbox("🎯 원하시는 요리 종류(카테고리)를 선택하세요:", categories)

# --- 추천 실행 버튼 ---
if st.button("🎲 오늘의 요리 추천받기!", type="primary", use_container_width=True):
    recommend_random_dish(selected_cat)
    st.balloons()  # 흥미를 돋우는 축하 폭죽 애니메이션

# --- 추천 결과 카드 영역 ---
if st.session_state.current_dish:
    dish = st.session_state.current_dish
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="dish-category">{dish["category"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dish-title">{dish["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'**"{dish["desc"]}"**')
    st.caption(f"💡 조리 꿀팁: {dish["tip"]}")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("👆 위 버튼을 눌러 오늘 먹을 요리를 뽑아보세요!")

# --- 최근 추천받은 메뉴 히스토리 ---
if st.session_state.history:
    st.write("##### 📜 최근 뽑은 메뉴 기록")
    st.write(" · ".join(st.session_state.history))
