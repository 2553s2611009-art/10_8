
import streamlit as st
from urllib.parse import quote
from datetime import datetime

# -----------------------------
# 기본 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="학생 교통 도우미",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# 디자인 설정
# -----------------------------
st.markdown("""
<style>
    .main {
        background-color: #F5F8FC;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(120deg, #246BFD, #54B7FF);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 20px;
    }

    .hero h1 {
        color: white;
        font-size: 34px;
    }

    .hero p {
        font-size: 17px;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #E6ECF5;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
    }

    .info-card {
        background-color: white;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #E6ECF5;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 세션 데이터
# -----------------------------
if "points" not in st.session_state:
    st.session_state.points = 0

if "records" not in st.session_state:
    st.session_state.records = []

# -----------------------------
# 사이드바 메뉴
# -----------------------------
st.sidebar.title("🚌 학생 교통 도우미")
st.sidebar.caption("안전하고 편리한 등하교를 위한 서비스")

page = st.sidebar.radio(
    "메뉴 선택",
    [
        "🏠 홈",
        "🗺️ 경로 찾기",
        "🚦 교통정보",
        "⭐ 포인트 기록",
        "🛡️ 안전 안내"
    ]
)

st.sidebar.divider()
st.sidebar.info(
    "이 앱은 교통정보 확인과 경로 검색을 돕는 서비스입니다. "
    "실제 교통 상황은 지도 서비스에서 확인하세요."
)

# -----------------------------
# 홈 화면
# -----------------------------
if page == "🏠 홈":
    st.markdown("""
    <div class="hero">
        <h1>🚌 학생 교통 도우미</h1>
        <p>오늘의 등교부터 안전한 귀가까지, 교통정보를 한곳에서 확인하세요!</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("⭐ 누적 포인트", f"{st.session_state.points}P")

    with col2:
        st.metric("📝 활동 기록", f"{len(st.session_state.records)}회")

    with col3:
        st.metric("📅 오늘 날짜", datetime.now().strftime("%Y-%m-%d"))

    st.subheader("📌 오늘의 등하교 체크리스트")

    check1 = st.checkbox("출발 전 버스·지하철 도착 정보 확인하기")
    check2 = st.checkbox("교통카드 잔액 확인하기")
    check3 = st.checkbox("횡단보도에서 신호 지키기")
    check4 = st.checkbox("하교 경로와 귀가 시간 확인하기")

    checked = sum([check1, check2, check3, check4])
    st.progress(checked / 4)
    st.caption(f"체크 완료: {checked}/4")

    st.divider()
    st.subheader("🚀 바로가기")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗺️ 경로 검색", use_container_width=True):
            st.session_state.quick_message = "경로 찾기 메뉴에서 출발지와 도착지를 입력하세요."

    with col2:
        if st.button("🚦 교통정보 확인", use_container_width=True):
            st.session_state.quick_message = "교통정보 메뉴에서 실시간 정보를 확인하세요."

    with col3:
        if st.button("🛡️ 안전수칙 보기", use_container_width=True):
            st.session_state.quick_message = "안전 안내 메뉴에서 교통안전 수칙을 확인하세요."

    if "quick_message" in st.session_state:
        st.info(st.session_state.quick_message)

# -----------------------------
# 경로 찾기
# -----------------------------
elif page == "🗺️ 경로 찾기":
    st.title("🗺️ 등하교 경로 찾기")
    st.write("출발지와 도착지를 입력하고 지도 서비스에서 경로를 확인하세요.")

    with st.form("route_form"):
        origin = st.text_input(
            "📍 출발지",
            placeholder="예: 학교 이름 또는 가까운 역"
        )

        destination = st.text_input(
            "🏁 도착지",
            placeholder="예: 도서관 또는 학원 이름"
        )

        transport = st.selectbox(
            "🚍 이동 수단",
            ["대중교통", "도보", "자전거", "자동차"]
        )

        provider = st.selectbox(
            "🗺️ 지도 서비스",
            ["Google 지도", "네이버 지도", "카카오맵"]
        )

        submitted = st.form_submit_button(
            "경로 검색하기",
            use_container_width=True
        )

    if submitted:
        if not origin.strip() or not destination.strip():
            st.warning("출발지와 도착지를 모두 입력해 주세요.")
        else:
            if provider == "Google 지도":
                mode = {
                    "대중교통": "transit",
                    "도보": "walking",
                    "자전거": "bicycling",
                    "자동차": "driving"
                }[transport]

                url = (
                    "https://www.google.com/maps/dir/?api=1"
                    f"&origin={quote(origin)}"
                    f"&destination={quote(destination)}"
                    f"&travelmode={mode}"
                )

            elif provider == "네이버 지도":
                url = (
                    "https://map.naver.com/p/search/"
                    f"{quote(origin + ' ' + destination + ' 경로')}"
                )

            else:
                url = (
                    "https://map.kakao.com/?q="
                    f"{quote(origin + ' ' + destination)}"
                )

            st.success("입력한 장소를 바탕으로 지도 검색 링크를 준비했어요.")
            st.link_button(
                f"{provider}에서 확인하기",
                url,
                use_container_width=True
            )

            st.caption(
                "지도 서비스에 따라 이동 수단이나 경로가 자동으로 "
                "설정되지 않을 수 있으니 검색 결과를 확인하세요."
            )

    st.info(
        "개인정보 보호를 위해 집 주소 대신 가까운 역이나 "
        "공공장소를 입력하는 것을 권장합니다."
    )

# -----------------------------
# 교통정보
# -----------------------------
elif page == "🚦 교통정보":
    st.title("🚦 교통정보 확인")
    st.write(
        "아래 서비스를 이용해 실시간 교통상황, 버스 도착 정보, "
        "도로 정체 등을 확인할 수 있어요."
    )

    st.subheader("🔎 교통정보 서비스")

    st.markdown("""
    <div class="info-card">
        <h4>🚦 국가교통정보센터</h4>
        도로 소통 상황과 교통 통제 정보를 확인할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
    st.link_button(
        "국가교통정보센터 열기",
        "https://www.its.go.kr/",
        use_container_width=True
    )

    st.markdown("""
    <div class="info-card">
        <h4>🗺️ 네이버 지도</h4>
        대중교통 경로와 지도 정보를 검색할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
    st.link_button(
        "네이버 지도 열기",
        "https://map.naver.com/",
        use_container_width=True
    )

    st.markdown("""
    <div class="info-card">
        <h4>🚏 카카오맵</h4>
        장소 검색과 대중교통 경로를 확인할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
    st.link_button(
        "카카오맵 열기",
        "https://map.kakao.com/",
        use_container_width=True
    )

    st.warning(
        "이 앱은 교통정보를 직접 수집하지 않습니다. "
        "최신 버스 도착 시간과 도로 상황은 연결된 서비스에서 확인하세요."
    )

# -----------------------------
# 포인트 기록
# -----------------------------
elif page == "⭐ 포인트 기록":
    st.title("⭐ 교통 포인트 기록")
    st.write("교통안전과 친환경 이동 습관을 기록해 보세요.")

    st.metric("현재 누적 포인트", f"{st.session_state.points}P")

    activities = {
        "🚌 대중교통 이용": 10,
        "🚶 안전하게 걷기": 5,
        "🚲 안전하게 자전거 이용": 10,
        "👥 카풀 이용": 8
    }

    st.subheader("활동 기록하기")

    for activity, point in activities.items():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"{activity} — {point}P")

        with col2:
            if st.button("기록하기", key=activity, use_container_width=True):
                st.session_state.points += point
                st.session_state.records.append({
                    "활동": activity,
                    "포인트": point,
                    "시간": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.rerun()

    st.divider()
    st.subheader("📋 나의 활동 내역")

    if st.session_state.records:
        st.dataframe(
            list(reversed(st.session_state.records)),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("아직 기록이 없습니다. 활동을 선택해 기록해 보세요.")

    st.caption(
        "포인트는 앱 체험용 가상 점수이며 실제 보상이나 교통비 할인과는 관계없습니다. "
        "현재 세션이 종료되면 기록이 사라질 수 있습니다."
    )

    if st.button("기록 초기화"):
        st.session_state.points = 0
        st.session_state.records = []
        st.rerun()

# -----------------------------
# 안전 안내
# -----------------------------
elif page == "🛡️ 안전 안내":
    st.title("🛡️ 교통안전 안내")
    st.write("안전한 등하교를 위해 아래 수칙을 확인하세요.")

    with st.expander("🚶 보행자 안전수칙", expanded=True):
        st.markdown("""
        - 횡단보도에서는 보행 신호를 확인하세요.
        - 길을 건널 때 휴대전화 화면을 보지 마세요.
        - 주차된 차량 주변에서는 움직이는 차량을 주의하세요.
        - 신호가 깜빡이면 무리하게 건너지 마세요.
        """)

    with st.expander("🚲 자전거 안전수칙"):
        st.markdown("""
        - 자전거를 탈 때 헬멧 등 보호장비를 착용하세요.
        - 야간에는 잘 보이는 조명과 반사 장비를 사용하세요.
        - 보행자와 안전거리를 유지하세요.
        - 교통법규와 자전거도로 이용 규칙을 지키세요.
        """)

    with st.expander("🚌 대중교통 안전수칙"):
        st.markdown("""
        - 버스가 완전히 정차한 뒤 승하차하세요.
        - 승강장 안전선 안쪽에서 기다리세요.
        - 버스나 지하철 안에서는 손잡이를 잡으세요.
        - 승하차 시 주변 사람과 차량을 살피세요.
        """)

    with st.expander("🔐 개인정보 및 정보 이용 안내"):
        st.markdown("""
        - 집 주소나 전화번호 같은 개인정보를 입력하지 마세요.
        - 이 앱은 실제 교통정보를 직접 제공하지 않습니다.
        - 지도 서비스의 검색 결과와 도착 정보를 확인한 뒤 이동하세요.
        - 실제 교통상황에 따라 경로와 소요 시간은 달라질 수 있습니다.
        """)

# -----------------------------
# 하단 안내
# -----------------------------
st.divider()
st.caption(
    "학생 교통 도우미 | 안전한 등하교를 위한 정보 안내 서비스"
)
