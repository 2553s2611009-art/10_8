
import streamlit as st
import requests
from urllib.parse import quote
from datetime import datetime

# =====================================
# 1. 기본 설정
# =====================================
st.set_page_config(
    page_title="학생 교통 도우미",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = "https://apis.data.go.kr/1613000"

try:
    API_KEY = st.secrets["serviceKey"]
except Exception:
    API_KEY = ""

try:
    MANUAL_CITY_CODE = str(st.secrets.get("city_code", "")).strip()
except Exception:
    MANUAL_CITY_CODE = ""

# =====================================
# 2. 디자인
# =====================================
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(120deg, #246BFD, #54B7FF);
        padding: 28px;
        border-radius: 18px;
        color: white;
        margin-bottom: 20px;
    }

    .hero h1 {
        color: white;
        font-size: 32px;
    }

    .hero p {
        font-size: 16px;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border: 1px solid #E6ECF5;
        border-radius: 12px;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# 3. 세션 데이터
# =====================================
if "points" not in st.session_state:
    st.session_state.points = 0

if "records" not in st.session_state:
    st.session_state.records = []

# =====================================
# 4. API 공통 함수
# =====================================
def api_request(service, operation, params):
    """공공데이터포털 API를 요청하고 JSON 응답을 반환한다."""
    if not API_KEY:
        raise RuntimeError(
            "API 인증키가 없습니다. Streamlit Secrets를 설정해 주세요."
        )

    url = f"{API_BASE}/{service}/{operation}"

    query = {
        "serviceKey": API_KEY,
        "_type": "json",
        "pageNo": 1,
        "numOfRows": 100,
        **params
    }

    try:
        response = requests.get(
            url,
            params=query,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError("API 응답 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.")
    except requests.exceptions.RequestException:
        raise RuntimeError("API 서버에 연결하지 못했습니다.")
    except ValueError:
        raise RuntimeError(
            "API가 JSON이 아닌 응답을 반환했습니다. 인증키와 API 신청 상태를 확인해 주세요."
        )

    # 공공데이터포털의 일반적인 응답 구조 확인
    response_body = data.get("response", {})
    header = response_body.get("header", {})

    result_code = str(header.get("resultCode", "00"))
    result_msg = str(header.get("resultMsg", ""))

    if result_code not in ("00", "0"):
        raise RuntimeError(
            f"API 오류: {result_msg or result_code}. "
            "인증키, 이용 권한, 요청 조건을 확인해 주세요."
        )

    body = response_body.get("body", {})
    items = body.get("items", {})

    if isinstance(items, dict):
        items = items.get("item", [])

    if items is None or items == "":
        return []

    if isinstance(items, dict):
        return [items]

    if isinstance(items, list):
        return items

    return []


def find_city_code():
    """도시코드 목록에서 천안시 코드를 찾는다."""
    if MANUAL_CITY_CODE:
        return MANUAL_CITY_CODE

    # TAGO 도시코드 목록 조회
    try:
        items = api_request(
            "BusSttnInfoInqireService",
            "getCtyCodeList",
            {}
        )

        for item in items:
            city_name = str(
                item.get("cityname", item.get("cityName", ""))
            )
            city_code = item.get("citycode", item.get("cityCode"))

            if "천안" in city_name and city_code:
                return str(city_code)

    except Exception:
        pass

    return None


def display_api_error(error):
    st.error(str(error))


# =====================================
# 5. 사이드바
# =====================================
st.sidebar.title("🚌 학생 교통 도우미")
st.sidebar.caption("안전하고 편리한 등하교")

page = st.sidebar.radio(
    "메뉴 선택",
    [
        "🏠 홈",
        "🚍 실시간 버스 정보",
        "🗺️ 경로 찾기",
        "⭐ 포인트 기록",
        "🛡️ 안전 안내"
    ]
)

st.sidebar.divider()
st.sidebar.caption("천안시 버스정보 API 연동")

# =====================================
# 6. 홈
# =====================================
if page == "🏠 홈":
    st.markdown("""
    <div class="hero">
        <h1>🚌 학생 교통 도우미</h1>
        <p>천안시 버스 도착정보와 경로를 편리하게 확인하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("⭐ 누적 포인트", f"{st.session_state.points}P")

    with c2:
        st.metric("📝 활동 기록", f"{len(st.session_state.records)}회")

    with c3:
        st.metric("📍 서비스 지역", "천안시")

    st.subheader("🚍 실시간 버스 정보")
    st.write(
        "정류소 이름으로 버스 도착 예정 시간을 확인하거나, "
        "버스 번호로 운행 위치를 검색할 수 있습니다."
    )

    if st.button("버스 정보 조회하기", use_container_width=True):
        st.session_state.open_bus_page = True
        st.rerun()

    if st.session_state.get("open_bus_page", False):
        st.info("왼쪽 메뉴에서 '실시간 버스 정보'를 선택하세요.")

    st.subheader("📌 이용 안내")
    st.markdown("""
    - **버스 도착정보:** 정류소별 도착 예정 시간과 남은 정류장 수
    - **버스 위치:** API가 제공하는 노선별 차량 위치 정보
    - **경로 찾기:** 외부 지도 서비스로 이동 경로 검색
    """)

    st.caption(
        "실시간 정보는 API 응답에 따라 달라집니다. "
        "운행이 없거나 데이터가 제공되지 않으면 결과가 표시되지 않을 수 있습니다."
    )

# =====================================
# 7. 실시간 버스 정보
# =====================================
elif page == "🚍 실시간 버스 정보":
    st.title("🚍 천안시 실시간 버스 정보")
    st.write("정류소나 버스 번호로 실제 API 데이터를 조회하세요.")

    if not API_KEY:
        st.warning(
            "아직 API 인증키가 설정되지 않았습니다. "
            "아래의 인증키 발급 및 Secrets 설정 방법을 먼저 진행해 주세요."
        )
        st.link_button(
            "공공데이터포털 버스 도착정보 API",
            "https://www.data.go.kr/data/15098530/openapi.do"
        )
        st.link_button(
            "공공데이터포털 버스정류소정보 API",
            "https://www.data.go.kr/data/15098534/openapi.do"
        )
        st.stop()

    city_code = None
    try:
        city_code = find_city_code()
    except Exception:
        city_code = None

    if not city_code:
        st.error(
            "천안시 도시코드를 확인하지 못했습니다. "
            "공공데이터포털의 TAGO 도시코드 목록을 확인한 후 "
            "Secrets의 city_code 항목에 정확한 코드를 입력해 주세요."
        )
        st.link_button(
            "TAGO 버스정류소 API 안내",
            "https://www.data.go.kr/data/15098534/openapi.do"
        )
        st.stop()

    st.caption(f"조회 도시코드: {city_code}")

    tab1, tab2 = st.tabs([
        "📍 정류소 검색 및 도착정보",
        "🚌 버스 번호 및 위치 검색"
    ])

    # ---------------------------------
    # 탭 1: 정류소 검색
    # ---------------------------------
    with tab1:
        st.subheader("정류소 이름 검색")

        with st.form("station_search_form"):
            station_keyword = st.text_input(
                "정류소 이름",
                placeholder="예: 천안역"
            )
            station_submit = st.form_submit_button(
                "정류소 검색",
                use_container_width=True
            )

        if station_submit:
            if not station_keyword.strip():
                st.warning("정류소 이름을 입력해 주세요.")
            else:
                try:
                    stations = api_request(
                        "BusSttnInfoInqireService",
                        "getSttnNmList",
                        {
                            "cityCode": city_code,
                            "nodeNm": station_keyword.strip()
                        }
                    )

                    # 검색어가 포함된 정류소만 표시
                    stations = [
                        s for s in stations
                        if station_keyword.strip() in str(
                            s.get("nodenm", s.get("nodeNm", ""))
                        )
                    ]

                    if not stations:
                        st.info(
                            "검색 결과가 없습니다. 다른 정류소 이름을 입력하거나 "
                            "API에서 해당 지역 정류소를 제공하는지 확인해 주세요."
                        )
                    else:
                        st.session_state.station_results = stations
                        st.success(f"정류소 {len(stations)}개를 찾았습니다.")

                except Exception as e:
                    display_api_error(e)

        stations = st.session_state.get("station_results", [])

        if stations:
            station_options = {}

            for s in stations:
                name = s.get("nodenm", s.get("nodeNm", "이름 미제공"))
                node_id = s.get("nodeid", s.get("nodeId", ""))
                number = s.get(" nodeno", s.get("nodeno", s.get("nodeNo", "")))

                label = f"{name}"
                if number:
                    label += f" (정류소 번호: {number})"
                if node_id:
                    label += f" | ID: {node_id}"

                station_options[label] = s

            selected_label = st.selectbox(
                "정류소 선택",
                list(station_options.keys())
            )
            selected_station = station_options[selected_label]

            if st.button(
                "이 정류소의 도착정보 조회",
                use_container_width=True
            ):
                node_id = selected_station.get(
                    "nodeid",
                    selected_station.get("nodeId", "")
                )

                if not node_id:
                    st.error("선택한 정류소의 ID가 응답에 없습니다.")
                else:
                    try:
                        arrivals = api_request(
                            "ArvlInfoInqireService",
                            "getSttnAcctoArvlPrearngeInfoList",
                            {
                                "cityCode": city_code,
                                "nodeId": node_id
                            }
                        )

                        if not arrivals:
                            st.info(
                                "현재 API에서 이 정류소의 도착정보를 제공하지 않습니다."
                            )
                        else:
                            st.subheader("🕒 실제 도착 예정 정보")

                            rows = []
                            for a in arrivals:
                                seconds = a.get("arrtime")
                                try:
                                    minutes = round(float(seconds) / 60)
                                    arrival_text = f"약 {minutes}분 후"
                                except (TypeError, ValueError):
                                    arrival_text = "정보 없음"

                                rows.append({
                                    "버스 번호": a.get(
                                        "routeno",
                                        a.get("routeNo", "정보 없음")
                                    ),
                                    "노선 유형": a.get(
                                        "routetp",
                                        a.get("routeTp", "정보 없음")
                                    ),
                                    "도착 예정": arrival_text,
                                    "남은 정류장": a.get(
                                        "arrprevstationcnt",
                                        a.get("arrPrevStationCnt", "정보 없음")
                                    ),
                                    "차량 유형": a.get(
                                        "vehicletp",
                                        a.get("vehicletp", "정보 없음")
                                    )
                                })

                            st.dataframe(
                                rows,
                                use_container_width=True,
                                hide_index=True
                            )
                            st.caption(
                                "도착 시간은 API가 제공한 초 단위 값을 분으로 환산한 것입니다. "
                                "실제 도착 시각과 차이가 날 수 있습니다."
                            )

                    except Exception as e:
                        display_api_error(e)

    # ---------------------------------
    # 탭 2: 버스 번호 검색 및 위치
    # ---------------------------------
    with tab2:
        st.subheader("버스 번호 검색")

        with st.form("route_search_form"):
            route_keyword = st.text_input(
                "버스 번호",
                placeholder="예: 1, 12, 900"
            )
            route_submit = st.form_submit_button(
                "버스 검색",
                use_container_width=True
            )

        if route_submit:
            if not route_keyword.strip():
                st.warning("버스 번호를 입력해 주세요.")
            else:
                try:
                    routes = api_request(
                        "RouteInfoInqireService",
                        "getRouteNoList",
                        {
                            "cityCode": city_code,
                            "routeNo": route_keyword.strip()
                        }
                    )

                    routes = [
                        r for r in routes
                        if route_keyword.strip() in str(
                            r.get("routeno", r.get("routeNo", ""))
                        )
                    ]

                    if not routes:
                        st.info(
                            "검색 결과가 없습니다. 버스 번호를 확인하거나 "
                            "천안시 노선 데이터 제공 여부를 확인해 주세요."
                        )
                    else:
                        st.session_state.route_results = routes
                        st.success(f"노선 {len(routes)}개를 찾았습니다.")

                except Exception as e:
                    display_api_error(e)

        routes = st.session_state.get("route_results", [])

        if routes:
            route_options = {}

            for r in routes:
                number = r.get("routeno", r.get("routeNo", "이름 미제공"))
                route_id = r.get("routeid", r.get("routeId", ""))
                route_type = r.get("routetp", r.get("routeTp", ""))

                label = f"{number}"
                if route_type:
                    label += f" ({route_type})"
                if route_id:
                    label += f" | ID: {route_id}"

                route_options[label] = r

            route_label = st.selectbox(
                "노선 선택",
                list(route_options.keys())
            )
            selected_route = route_options[route_label]

            if st.button(
                "실시간 버스 위치 조회",
                use_container_width=True
            ):
                route_id = selected_route.get(
                    "routeid",
                    selected_route.get("routeId", "")
                )

                if not route_id:
                    st.error("선택한 노선의 ID가 응답에 없습니다.")
                else:
                    try:
                        locations = api_request(
                            "BusLcInfoInqireService",
                            "getRouteAcctoBusLcList",
                            {
                                "cityCode": city_code,
                                "routeId": route_id
                            }
                        )

                        if not locations:
                            st.info(
                                "현재 운행 중인 버스 위치가 없거나 "
                                "API에서 위치 데이터를 제공하지 않습니다."
                            )
                        else:
                            st.subheader("📍 실제 버스 위치")

                            rows = []
                            map_rows = []

                            for bus in locations:
                                lat = bus.get("gpslati")
                                lon = bus.get("gpslong")

                                rows.append({
                                    "버스 번호": bus.get(
                                        "routenm",
                                        bus.get("routeNm", "정보 없음")
                                    ),
                                    "현재 정류소": bus.get(
                                        "nodenm",
                                        bus.get("nodeNm", "정보 없음")
                                    ),
                                    "정류소 순서": bus.get(
                                        "nodeord",
                                        bus.get("nodeOrd", "정보 없음")
                                    ),
                                    "차량 번호": bus.get(
                                        "vehicleno",
                                        bus.get("vehicleNo", "정보 없음")
                                    ),
                                    "위도": lat or "정보 없음",
                                    "경도": lon or "정보 없음"
                                })

                                try:
                                    if lat and lon:
                                        map_rows.append({
                                            "lat": float(lat),
                                            "lon": float(lon)
                                        })
                                except (TypeError, ValueError):
                                    pass

                            st.dataframe(
                                rows,
                                use_container_width=True,
                                hide_index=True
                            )

                            if map_rows:
                                st.subheader("🗺️ 위치 지도")
                                st.map(map_rows, latitude="lat", longitude="lon")

                            st.caption(
                                "지도는 API가 좌표를 제공한 차량만 표시합니다. "
                                "좌표가 없는 차량은 표에만 나타날 수 있습니다."
                            )

                    except Exception as e:
                        display_api_error(e)

    if st.button("🔄 검색 결과 초기화"):
        st.session_state.station_results = []
        st.session_state.route_results = []
        st.rerun()

# =====================================
# 8. 경로 검색
# =====================================
elif page == "🗺️ 경로 찾기":
    st.title("🗺️ 등하교 경로 찾기")

    with st.form("route_form"):
        origin = st.text_input(
            "📍 출발지",
            placeholder="예: 천안역"
        )
        destination = st.text_input(
            "🏁 도착지",
            placeholder="예: 학교 이름"
        )
        transport = st.selectbox(
            "이동 수단",
            ["대중교통", "도보", "자전거", "자동차"]
        )
        provider = st.selectbox(
            "지도 서비스",
            ["Google 지도", "네이버 지도", "카카오맵"]
        )
        submitted = st.form_submit_button(
            "경로 검색",
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

            st.link_button(
                f"{provider}에서 경로 확인",
                url,
                use_container_width=True
            )

    st.info("지도 서비스에 따라 경로와 이동 수단을 직접 선택해야 할 수 있습니다.")

# =====================================
# 9. 포인트 기록
# =====================================
elif page == "⭐ 포인트 기록":
    st.title("⭐ 교통 포인트 기록")
    st.metric("현재 누적 포인트", f"{st.session_state.points}P")

    activities = {
        "🚌 대중교통 이용": 10,
        "🚶 안전하게 걷기": 5,
        "🚲 안전하게 자전거 이용": 10,
        "👥 카풀 이용": 8
    }

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

    if st.session_state.records:
        st.subheader("📋 활동 내역")
        st.dataframe(
            list(reversed(st.session_state.records)),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("아직 기록된 활동이 없습니다.")

    st.caption("포인트는 체험용 가상 점수이며 실제 보상이나 할인과 관계없습니다.")

    if st.button("기록 초기화"):
        st.session_state.points = 0
        st.session_state.records = []
        st.rerun()

# =====================================
# 10. 안전 안내
# =====================================
elif page == "🛡️ 안전 안내":
    st.title("🛡️ 교통안전 안내")

    with st.expander("🚶 보행자 안전", expanded=True):
        st.markdown("""
        - 횡단보도에서 신호를 확인하세요.
        - 길을 건널 때 휴대전화 화면을 보지 마세요.
        - 버스 앞뒤로 무리하게 횡단하지 마세요.
        """)

    with st.expander("🚌 대중교통 안전"):
        st.markdown("""
        - 버스가 완전히 정차한 뒤 승하차하세요.
        - 승강장 안전선 안쪽에서 기다리세요.
        - 차량 안에서는 손잡이를 잡으세요.
        """)

    with st.expander("🔐 개인정보와 실시간 정보"):
        st.markdown("""
        - 집 주소와 전화번호 같은 개인정보를 입력하지 마세요.
        - API에 데이터가 없으면 앱에서도 실제 정보를 확인할 수 없습니다.
        - 도착 예정 시간은 교통 상황에 따라 달라질 수 있습니다.
        - API 인증키를 공개 GitHub 저장소에 올리지 마세요.
        """)

# =====================================
# 11. 하단
# =====================================
st.divider()
st.caption("학생 교통 도우미 | 천안시 버스정보 연동 버전")
