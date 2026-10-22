import streamlit as st
from urllib.parse import quote
from datetime import datetime

st.set_page_config(
    page_title="길잇다 | 스마트 교통 도우미",
    page_icon="🚌",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background: #f4f7fb; }
.hero {
    background: linear-gradient(120deg, #103b5c, #117a8b);
    color: white; padding: 1.7rem; border-radius: 18px;
}
.hero h1 { color: white; }
.hero p { color: #eaf7fb; }
.card {
    background: white; padding: 1rem; border-radius: 14px;
    border: 1px solid #e0e8f0; min-height: 120px;
}
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "points" not in st.session_state:
    st.session_state.points = 0
if "records" not in st.session_state:
    st.session_state.records = []

def make_route_url(origin, destination, mode, provider):
    """지도 서비스의 경로 확인 URL 생성"""
    origin = quote(origin, safe="")
    destination = quote(destination, safe="")

    if provider == "Google 지도":
        travel = {
            "대중교통": "transit",
            "자동차": "driving",
            "도보": "walking",
        }[mode]
        return (
            "https://www.google.com/maps/dir/?api=1"
            f"&origin={origin}&destination={destination}"
            f"&travelmode={travel}"
        )

    if provider == "네이버 지도":
        mode_slug = {
            "대중교통": "transit",
            "자동차": "car",
            "도보": "walk",
        }[mode]
        return (
            f"https://map.naver.com/p/directions/"
            f"{origin}/{destination}/-/{mode_slug}"
        )

    return (
        f"https://map.kakao.com/"
        f"?sName={origin}&eName={destination}"
    )

st.sidebar.title("🚌 길잇다")
st.sidebar.caption("교통은 편리하게, 이동은 더 똑똑하게")

page = st.sidebar.radio(
    "메뉴",
    ["홈 대시보드", "실시간 교통정보", "포인트 안내", "앱 사용 안내"],
)

if page == "홈 대시보드":
    st.markdown("""
    <div class="hero">
      <h1>길잇다 🚌</h1>
      <p>교통 상황을 확인하고 더 나은 이동을 선택해 보세요.</p>
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3)
    a.metric("보유 포인트", f"{st.session_state.points:,} P")
    b.metric("실천 기록", f"{len(st.session_state.records)}건")
    c.metric("핵심 목표", "혼잡 완화")

    st.subheader("주요 기능")
    x, y, z = st.columns(3)

    with x:
        st.markdown("""
        <div class="card">
        <h3>🚦 교통정보</h3>
        출발지와 도착지를 입력하고 지도에서 경로를 확인하세요.
        </div>
        """, unsafe_allow_html=True)

    with y:
        st.markdown("""
        <div class="card">
        <h3>🌱 포인트</h3>
        대중교통과 친환경 이동 실천을 기록하세요.
        </div>
        """, unsafe_allow_html=True)

    with z:
        st.markdown("""
        <div class="card">
        <h3>📘 사용 안내</h3>
        메뉴별 사용 방법과 주의사항을 확인하세요.
        </div>
        """, unsafe_allow_html=True)

    st.subheader("교통문제를 줄이는 작은 실천")
    st.markdown("""
    - 출발 전에 여러 경로를 비교하기
    - 가능한 경우 버스와 지하철 이용하기
    - 가까운 거리는 걷거나 자전거 이용하기
    - 가능하다면 혼잡한 시간대 피하기
    """)

elif page == "실시간 교통정보":
    st.title("🚦 실시간 교통정보")
    st.info(
        "이 앱은 실시간 도로 데이터를 직접 수집하지 않습니다. "
        "외부 지도 및 교통정보 사이트에서 최신 상황을 확인하세요."
    )

    with st.form("route_form"):
        origin = st.text_input("출발지", placeholder="예: 천안역")
        destination = st.text_input("도착지", placeholder="예: 천안시청")
        mode = st.selectbox(
            "이동 수단", ["대중교통", "자동차", "도보"]
        )
        provider = st.selectbox(
            "지도 서비스", ["네이버 지도", "Google 지도", "카카오맵"]
        )
        submitted = st.form_submit_button(
            "경로 확인하기", type="primary"
        )

    if submitted:
        origin = origin.strip()
        destination = destination.strip()

        if not origin or not destination:
            st.error("출발지와 도착지를 모두 입력해 주세요.")
        elif origin.casefold() == destination.casefold():
            st.warning("출발지와 도착지가 같습니다.")
        else:
            try:
                url = make_route_url(
                    origin, destination, mode, provider
                )
                st.success("경로 링크를 만들었습니다.")
                st.link_button(
                    f"{provider}에서 경로 열기",
                    url,
                    type="primary",
                )
            except (ValueError, KeyError):
                st.error("입력한 정보를 확인하고 다시 시도해 주세요.")
            except Exception:
                st.error("링크 생성 중 오류가 발생했습니다.")

    st.divider()
    st.subheader("교통정보 사이트")

    st.link_button(
        "국가교통정보센터 (ITS)",
        "https://www.its.go.kr/",
    )
    st.link_button(
        "서울 TOPIS",
        "https://topis.seoul.go.kr/",
    )

elif page == "포인트 안내":
    st.title("🌱 포인트 사용 안내")
    st.warning(
        "포인트는 교육용 가상 점수입니다. "
        "현금이나 실제 교통 마일리지로 교환되지 않습니다."
    )

    st.metric("현재 포인트", f"{st.session_state.points:,} P")

    rules = {
        "버스·지하철 이용": 10,
        "도보 이동": 5,
        "자전거 이용": 10,
        "카풀 이용": 8,
    }

    with st.form("points_form"):
        activity = st.selectbox("실천한 이동", list(rules.keys()))
        count = st.number_input(
            "횟수", min_value=1, max_value=10, value=1, step=1
        )
        add = st.form_submit_button("포인트 적립 기록")

    if add:
        earned = rules[activity] * int(count)
        st.session_state.points += earned
        st.session_state.records.insert(0, {
            "기록 시각": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "이동 실천": activity,
            "횟수": int(count),
            "적립 포인트": earned,
        })
        st.success(f"{earned}P를 기록했습니다.")

    st.subheader("포인트 이용 방법")
    st.markdown("""
    1. 실제로 실천한 이동 방법을 선택합니다.
    2. 횟수를 입력합니다.
    3. 적립 버튼을 누릅니다.
    4. 아래에서 기록을 확인합니다.
    """)

    if st.session_state.records:
        st.dataframe(
            st.session_state.records,
            use_container_width=True,
            hide_index=True,
        )
        if st.button("포인트와 기록 초기화"):
            st.session_state.points = 0
            st.session_state.records = []
            st.rerun()
    else:
        st.caption("아직 기록이 없습니다.")

elif page == "앱 사용 안내":
    st.title("📘 앱 사용 안내")

    with st.expander("1. 교통정보 확인", expanded=True):
        st.write(
            "출발지와 도착지를 입력하고 이동 수단과 지도 서비스를 "
            "선택한 뒤 경로 확인 버튼을 누르세요."
        )

    with st.expander("2. 포인트 기록"):
        st.write(
            "포인트 안내에서 이동 실천을 선택하고 적립 버튼을 누르세요. "
            "포인트는 시연용 가상 점수입니다."
        )

    with st.expander("3. 교통문제 해결에 활용하기"):
        st.write(
            "여러 경로를 비교하고 대중교통, 도보, 자전거 등을 "
            "활용해 자동차 이용과 교통 혼잡을 줄이는 데 동참하세요."
        )

    with st.expander("4. 데이터 및 개인정보"):
        st.write(
            "앱은 현재 위치를 자동 수집하지 않습니다. "
            "입력한 장소는 외부 지도 링크 생성에 사용됩니다. "
            "포인트는 세션이 끝나면 초기화될 수 있습니다."
        )

st.sidebar.divider()
st.sidebar.caption("길잇다 | 교통문제 해결 프로젝트")
st.sidebar.caption("교육용 프로토타입")
