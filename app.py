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

# 밝고 따뜻한 오렌지/크림 톤의 디자인 CSS
CUSTOM_CSS = """
<style>
    /* 전체 배경색: 따뜻한 크림/연노랑 */
    .stApp {
        background-color: #fffbf0;
    }

    /* 추천 결과 메인 카드 (중앙 강조 배치) */
    .result-card {
        background-color: #ffffff;
        padding: 2.5rem 2rem;
        border-radius: 24px;
        box-shadow: 0 12px 30px rgba(217, 119, 6, 0.12);
        border: 2px solid #fde68a;
        text-align: center;
        margin: 1.5rem 0;
    }

    /* 요리 이름 텍스트 (CSS clamp로 화면 크기에 따라 반응형 자동 조절) */
    .dish-title {
        font-weight: 800;
        font-size: clamp(2.2rem, 8vw, 3.8rem);
        color: #d97706; /* 오렌지 브라운 */
        margin: 0.5rem 0;
        line-height: 1.2;
    }

    /* 카테고리 태그 스타일 */
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
# 2. 확장된 요리 메뉴 데이터베이스 (30가지)
# ==========================================
DISHES_DATABASE = [
    # --- 한식 🇰🇷 ---
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
        "name": "🥩 제육볶음",
        "category": "한식 🇰🇷",
        "desc": "매콤달콤한 양념에 불향이 가득한 밥도둑",
        "tip": "상추나 깻잎과 함께 쌈을 싸서 먹으면 최고예요."
    },
    {
        "name": "🥣 닭볶음탕",
        "category": "한식 🇰🇷",
        "desc": "칼칼한 양념과 포슬포슬한 감자의 환상 조합",
        "tip": "국물을 밥에 자작하게 비벼 먹는 것을 추천합니다."
    },
    {
        "name": "🍚 비빔밥",
        "category": "한식 🇰🇷",
        "desc": "각종 나물과 고추장, 참기름의 고소한 풍미",
        "tip": "계란후라이는 반숙으로 올려 노른자를 터뜨려 드세요."
    },
    {
        "name": "🥩 불고기",
        "category": "한식 🇰🇷",
        "desc": "달콤하고 짭조름한 양념이 매력적인 잔칫날 요리",
        "tip": "당면을 넣어서 함께 조리면 더 맛있습니다."
    },

    # --- 일식 🇯🇵 ---
    {
        "name": "🍛 카레라이스",
        "category": "일식 🇯🇵",
        "desc": "진하고 진득한 풍미로 한 그릇 뚝딱 비우는 메뉴",
        "tip": "양파를 갈색이 될 때까지 오래 볶으면 풍미가 깊어집니다."
    },
    {
        "name": "🍱 돈까스",
        "category": "일식 🇯🇵",
        "desc": "바삭한 튀김옷 속 촉촉한 육즙이 살아있는 메뉴",
        "tip": "양배추 샐러드와 겨자 소스를 살짝 곁들여보세요."
    },
    {
        "name": "🍣 초밥",
        "category": "일식 🇯🇵",
        "desc": "신선한 회와 새콤달콤한 밥의 정갈한 조화",
        "tip": "장국과 생강 절임을 함께 즐기면 더욱 깔끔합니다."
    },
    {
        "name": "🍜 라멘",
        "category": "일식 🇯🇵",
        "desc": "진하게 우려낸 육수와 쫄깃한 면발의 만남",
        "tip": "차슈와 온천계란(아지타마고) 추가는 필수!"
    },
    {
        "name": "🍚 가츠동",
        "category": "일식 🇯🇵",
        "desc": "달콤한 짭조름한 간장 소스에 계란을 풀어 올린 돈까스 덮밥",
        "tip": "계란을 너무 다 익히지 말고 부드럽게 익혀주세요."
    },

    # --- 양식 🍝 ---
    {
        "name": "🍝 알리오 올리오",
        "category": "양식 🇮🇹",
        "desc": "마늘과 올리브 오일의 고소하고 알싸한 풍미",
        "tip": "면수와 올리브 오일을 잘 섞어 유화시키는 것이 핵심!"
    },
    {
        "name": "🍝 까르보나라",
        "category": "양식 🇮🇹",
        "desc": "고소하고 진한 크림/계란 소스의 클래식 파스타",
        "tip": "베이컨을 바삭하게 볶아 올려 식감을 살려보세요."
    },
    {
        "name": "🍕 페퍼로니 피자",
        "category": "양식 🇮🇹",
        "desc": "짭조름한 페퍼로니와 쭈욱 늘어나는 치즈의 매력",
        "tip": "핫소스나 파마산 치즈 가루를 취향껏 더해보세요."
    },
    {
        "name": "🍔 수제 버거",
        "category": "양식 🇺🇸",
        "desc": "두툼한 패티와 신선한 야채가 가득한 입안 가득 행복",
        "tip": "감자튀김과 시원한 콜라를 함께 준비하세요."
    },
    {
        "name": "🥩 찹스테이크",
        "category": "양식 🇺🇸",
        "desc": "한 입 크기의 두툼한 고기와 달콤 짭조름한 소스",
        "tip": "파프리카, 양파, 버섯을 큼직하게 넣어 볶으세요."
    },

    # --- 중식 🇨🇳 ---
    {
        "name": "🥟 마라탕",
        "category": "중식 🇨🇳",
        "desc": "얼얼하고 매콤해서 스트레스가 싹 풀리는 중독성 메뉴",
        "tip": "좋아하는 버섯, 푸주, 분모자를 취향껏 넣어보세요."
    },
    {
        "name": "🍜 짜장면",
        "category": "중식 🇨🇳",
        "desc": "춘장의 고소함과 달콤함이 어우러진 국민 면 요리",
        "tip": "고춧가루를 살짝 뿌려 먹으면 느끼함을 잡아줍니다."
    },
    {
        "name": "🥣 짬뽕",
        "category": "중식 🇨🇳",
        "desc": "해산물과 야채가 들어간 칼칼하고 시원한 불맛 국물",
        "tip": "면을 다 먹고 밥을 말아 먹어도 별미입니다."
    },
    {
        "name": "🍗 탕수육",
        "category": "중식 🇨🇳",
        "desc": "바삭한 고기 튀김에 새콤달콤한 소스의 완벽 조합",
        "tip": "찍먹파와 부먹파의 취향을 사전에 조사하세요!"
    },
    {
        "name": "🔥 마파두부",
        "category": "중식 🇨🇳",
        "desc": "매콤한 양념에 두부의 부드러움이 어우러진 덮밥 요리",
        "tip": "밥 위에 가득 얹어 슥슥 비벼 드세요."
    },

    # --- 아시안 🌏 ---
    {
        "name": "🍜 쌀국수 (포)",
        "category": "아시안 🌏",
        "desc": "깊고 시원한 육수와 숙주의 아삭함이 일품인 베트남 요리",
        "tip": "칠리소스와 해선장 소스를 곁들여 풍미를 올려보세요."
    },
    {
        "name": "🍛 팟타이",
        "category": "아시안 🌏",
        "desc": "새콤달콤 매콤한 소스에 볶아낸 태국식 쌀국수",
        "tip": "땅콩 가루와 라임즙을 듬뿍 얹어 섞어 드세요."
    },
    {
        "name": "🍍 나시고랭",
        "category": "아시안 🌏",
        "desc": "단짠 소스와 해산물이 어우러진 인도네시아식 볶음밥",
        "tip": "반숙 계란후라이와 알새우칩을 곁들이면 완성도가 올라갑니다."
    },

    # --- 분식/간편식 ⚡ ---
    {
        "name": "떡볶이 🌶️",
        "category": "분식 🇰🇷",
        "desc": "매콤달콤 국민 간식이자 영원한 영혼의 음식",
        "tip": "삶은 계란, 어묵, 튀김을 국물에 찍어 드세요."
    },
    {
        "name": "🍳 햄 계란볶음밥",
        "category": "간편식 ⚡",
        "desc": "냉장고 파먹기에 딱 좋은 초간단 효자 메뉴",
        "tip": "파기름을 먼저 내고 찬밥을 눌러가며 볶아주세요."
    },
    {
        "name": "🥪 클럽 샌드위치",
        "category": "간편식 ⚡",
        "desc": "신선한 야채와 계란, 베이컨의 신선한 조합",
        "tip": "식빵 안쪽에 마요네즈를 바르면 야채 수분으로 눅눅해지지 않아요."
    },

    # --- 야식/디저트 🌙 ---
    {
        "name": "🍗 양념치킨",
        "category": "야식 🌙",
        "desc": "바삭한 튀김에 매콤달콤 양념 소스가 듬뿍!",
        "tip": "치킨무와 시원한 음료를 함께 준비하세요."
    },
    {
        "name": "🐖 족발",
        "category": "야식 🌙",
        "desc": "쫀득쫀득한 식감과 고소한 한약재 풍미의 조화",
        "tip": "막국수와 무김치를 함께 싸서 드세요."
    },
    {
        "name": "🧇 크로플 & 커피",
        "category": "디저트 ☕",
        "desc": "겉은 바삭 속은 촉촉한 크로플과 시원한 커피 한 잔",
        "tip": "바닐라 아이스크림이나 메이플 시럽을 올려보세요."
    }
]


# ==========================================
# 3. 세션 상태(st.session_state) 초기화
# ==========================================
if "current_dish" not in st.session_state:
    st.session_state.current_dish = None  # 현재 뽑힌 요리
if "history" not in st.session_state:
    st.session_state.history = []         # 최근 뽑은 요리 히스토리 (최대 5개)


# ==========================================
# 4. 요리 추천 로직 함수
# ==========================================
def recommend_random_dish(selected_category):
    """선택한 카테고리에 맞는 요리를 무작위로 추첨하는 함수"""
    # 1) 카테고리 필터링
    if selected_category == "전체":
        candidates = DISHES_DATABASE
    else:
        # 카테고리 문자열 포함 여부 체크 (예: "한식"으로 검색 시 "한식 🇰🇷" 매칭)
        search_term = selected_category.split()[0]
        candidates = [dish for dish in DISHES_DATABASE if search_term in dish["category"]]
    
    # 2) 무작위 뽑기 및 히스토리 저장
    if candidates:
        chosen = random.choice(candidates)
        st.session_state.current_dish = chosen
        
        # 최근 기록에 추가 (중복 방지 및 최근 5개 유지)
        if chosen["name"] not in st.session_state.history:
            st.session_state.history.insert(0, chosen["name"])
            if len(st.session_state.history) > 5:
                st.session_state.history.pop()


# ==========================================
# 5. 메인 앱 화면 구성
# ==========================================
st.title("🍽️ 오늘 뭐 먹지? 무작위 요리 추천기")
st.write("결정하기 어려울 땐 카테고리를 선택하고 아래 버튼을 눌러 오늘 먹을 요리를 뽑아보세요!")

st.divider()

# --- 카테고리 선택 셀렉트박스 ---
categories = ["전체", "한식 🇰🇷", "일식 🇯🇵", "양식 🍝", "중식 🇨🇳", "아시안 🌏", "분식 🇰🇷", "간편식 ⚡", "야식 🌙", "디저트 ☕"]
selected_cat = st.selectbox("🎯 원하시는 요리 카테고리를 선택하세요:", categories)

# --- 추천 실행 버튼 ---
if st.button("🎲 오늘의 요리 추천받기!", type="primary", use_container_width=True):
    recommend_random_dish(selected_cat)
    st.balloons()  # 축하 풍선 애니메이션 효과

# --- 추천 결과 출력 영역 ---
if st.session_state.current_dish:
    dish = st.session_state.current_dish
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="dish-category">{dish["category"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dish-title">{dish["name"]}</div>', unsafe_allow_html=True)
    st.markdown(f'**"{dish["desc"]}"**')
    st.caption(f"💡 조리 꿀팁: {dish["tip"]}")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("👆 위 버튼을 눌러 오늘 먹을 메뉴를 무작위로 뽑아보세요!")

# --- 최근 추천 목록 ---
if st.session_state.history:
    st.write("##### 📜 최근 뽑은 메뉴 기록")
    st.write(" · ".join(st.session_state.history))

# --- 최근 추천 목록 ---
if st.session_state.history:
    st.write("##### 📜 최근 뽑은 메뉴 기록")
    st.write(" · ".join(st.session_state.history))
