import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_config_title="청소년 교통비 지원 & 포인트 타운",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS로 디자인 및 버튼 모듈성 향상
st.markdown("""
    <style>
    /* 메인 타이틀 스타일 */
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    /* 카드 컴포넌트 스타일 */
    .card-box {
        background-color: #F8FAFC;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
    }
    /* 포인트 강조 스타일 */
    .point-highlight {
        font-size: 1.8rem;
        font-weight: 800;
        color: #2563EB;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태(Session State) 초기화
# -----------------------------------------------------------------------------
# 앱 실행 시 기본 데이터 설정 (데이터베이스 대체)
if "user_points" not in st_state:
    st.session_state.user_points = 18500  # 현재 보유 포인트

if "monthly_support" not in st.session_state:
    st.session_state.monthly_support = 30000  # 이번 달 지원금 한도

if "history" not in st.session_state:
    # 초기 내역 생성
    today = datetime.now()
    st.session_state.history = [
        {"날짜": (today - timedelta(days=4)).strftime("%Y-%m-%d %H:%M"), "구분": "교통 환급", "상세내용": "시내버스 탑승 (마일리지 적립)", "변동포인트": 500, "잔여포인트": 15500},
        {"날짜": (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), "구분": "사용", "상세내용": "CU 편의점 (바나나우유 외)", "변동포인트": -2500, "잔여포인트": 13000},
        {"날짜": (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "구분": "교통 환급", "상세내용": "지하철 1호선 (마일리지 적립)", "변동포인트": 600, "잔여포인트": 13600},
        {"날짜": (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "구분": "사용", "상세내용": "교보문고 (노트/펜)", "변동포인트": -3100, "잔여포인트": 10500},
        {"날짜": today.strftime("%Y-%m-%d %H:%M"), "구분": "교통 환급", "상세내용": "청소년 대중교통 분기 지원금", "변동포인트": 8000, "잔여포인트": 18500},
    ]

# -----------------------------------------------------------------------------
# 3. 메인 상단 헤더 및 [메인페이지로] 버튼
# -----------------------------------------------------------------------------
top_col1, top_col2 = st.columns([1, 4])

with top_col1:
    # 요청사항: 왼쪽 상단 메인페이지로 돌아가는 버튼
    if st.button("🏠 메인으로", use_container_width=True, help="클릭 시 화면이 초기화되며 메인페이지로 이동합니다."):
        st.toast("메인 화면으로 이동했습니다.", icon="✨")
        st.rerun()

with top_col2:
    st.markdown("<div class='main-title'>🚌 청소년 교통비 지원 & 제휴 포인트 타운</div>", unsafe_allow_html=True)

st.divider()

# -----------------------------------------------------------------------------
# 4. PC 화면 기준 3열 layout 설정 (3칸 구성)
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 1.1, 1.2])

# =============================================================================
# [1칸] 교통 포인트 현황
# =============================================================================
with col1:
    st.subheader("📊 1. 포인트 및 지원 현황")
    
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("**홍길동 청소년**님의 현재 잔여 포인트", unsafe_allow_html=True)
    st.markdown(f"<div class='point-highlight'>{st.session_state.user_points:,} P</div>", unsafe_allow_html=True)
    st.caption("※ 대중교통 이용 시 결제금액의 일부가 자동 적립됩니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 이번 달 환급/지원율 프로그레스 바
    used_support = min(st.session_state.user_points, st.session_state.monthly_support)
    progress_percent = min(int((used_support / st.session_state.monthly_support) * 100), 100)
    
    st.write(f"**이번 달 지원 한도 달성률 ({progress_percent}%)**")
    st.progress(progress_percent / 100)
    st.caption(f"월 최대 지원 한도: {st.session_state.monthly_support:,}원")

    # 대중교통 이용 적립 시뮬레이터 (추가 유용한 기능)
    st.markdown("---")
    st.markdown("##### 🚌 대중교통 이용 적립 시뮬레이션")
    st.caption("대중교통을 이용하면 마일리지 포인트가 추가 적립됩니다.")
    
    transport_type = st.selectbox("이용 교통수단 선택", ["시내버스 (500P 적립)", "지하철 (600P 적립)", "광역버스 (1,000P 적립)"])
    
    if st.button("교통카드 찍기 (적립)", use_container_width=True):
        earned_p = 0
        t_name = ""
        if "시내버스" in transport_type:
            earned_p = 500
            t_name = "시내버스 탑승"
        elif "지하철" in transport_type:
            earned_p = 600
            t_name = "지하철 탑승"
        else:
            earned_p = 1000
            t_name = "광역버스 탑승"
            
        st.session_state.user_points += earned_p
        
        # 내역 추가
        new_record = {
            "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "구분": "교통 환급",
            "상세내용": f"{t_name} (마일리지 적립)",
            "변동포인트": earned_p,
            "잔여포인트": st.session_state.user_points
        }
        st.session_state.history.insert(0, new_record)
        st.success(f"{earned_p:,}P가 성공적으로 적립되었습니다!")
        st.rerun()

# =============================================================================
# [2칸] 남은 포인트 사용하기 (편의점, 제휴처 등)
# =============================================================================
with col2:
    st.subheader("🏪 2. 제휴처 포인트 사용")
    st.caption("적립된 포인트를 편의점, 서점, 카페에서 상품권으로 교환하세요.")

    store_tab1, store_tab2, store_tab3 = st.tabs(["🛍️ 편의점", "📚 서점/문구", "☕ 카페/디저트"])

    # 제휴처별 상품 목록
    items_data = {
        "편의점": [
            {"name": "CU 모바일 금액권 3,000원", "price": 3000, "icon": "🏪"},
            {"name": "GS25 모바일 금액권 5,000원", "price": 5000, "icon": "🏪"},
            {"name": "세븐일레븐 바나나우유", "price": 1700, "icon": "🍌"},
        ],
        "서점/문구": [
            {"name": "교보문고 도서문화상품권 5,000원", "price": 5000, "icon": "📚"},
            {"name": "알라딘 3,000원 할인권", "price": 3000, "icon": "📖"},
            {"name": "문구점 스터디플래너 교환권", "price": 4000, "icon": "✏️"},
        ],
        "카페/디저트": [
            {"name": "메가커피 아이스 아메리카노", "price": 2000, "icon": "☕"},
            {"name": "빽다방 빽스치노", "price": 3800, "icon": "🥤"},
            {"name": "설빙 5,000원 모바일 쿠폰", "price": 5000, "icon": "🍨"},
        ]
    }

    def render_store_category(category_name):
        for idx, item in enumerate(items_data[category_name]):
            with st.container():
                c_a, c_b = st.columns([2.5, 1.5])
                with c_a:
                    st.markdown(f"**{item['icon']} {item['name']}**")
                    st.markdown(f"<span style='color:#2563EB; font-weight:bold;'>{item['price']:,} P</span>", unsafe_allow_html=True)
                with c_b:
                    if st.button("교환하기", key=f"{category_name}_{idx}"):
                        if st.session_state.user_points >= item['price']:
                            st.session_state.user_points -= item['price']
                            
                            # 내역 추가
                            new_record = {
                                "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "구분": "사용",
                                "상세내용": f"{item['name']} 사용",
                                "변동포인트": -item['price'],
                                "잔여포인트": st.session_state.user_points
                            }
                            st.session_state.history.insert(0, new_record)
                            st.balloons()
                            st.success("쿠폰이 교환되었습니다!")
                            st.rerun()
                        else:
                            st.error("포인트가 부족합니다.")
                st.divider()

    with store_tab1:
        render_store_category("편의점")
    with store_tab2:
        render_store_category("서점/문구")
    with store_tab3:
        render_store_category("카페/디저트")

# =============================================================================
# [3칸] 포인트 사용 내역 (적립/사용 상세)
# =============================================================================
with col3:
    st.subheader("📜 3. 포인트 이용 내역")
    
    # 데이터프레임 변환 및 예외처리
    try:
        df = pd.DataFrame(st.session_state.history)
        
        if not df.empty:
            # 포인트 변환 표시 가공 (+ / - 붙이기)
            df_display = df.copy()
            df_display["변동포인트(P)"] = df_display["변동포인트"].apply(
                lambda x: f"+{x:,}" if x > 0 else f"{x:,}"
            )
            df_display["잔여포인트(P)"] = df_display["잔여포인트"].apply(lambda x: f"{x:,}")

            # 최근 내역 테이블
            st.dataframe(
                df_display[["날짜", "구분", "상세내용", "변동포인트(P)", "잔여포인트(P)"]],
                use_container_width=True,
                hide_index=True,
                height=240
            )

            # 시각화 차트 (포인트 흐름)
            st.markdown("##### 📈 이용 유형별 통계")
            type_counts = df["구분"].value_counts().reset_index()
            type_counts.columns = ["구분", "건수"]

            fig = px.pie(
                type_counts, 
                values="건수", 
                names="구분", 
                color="구분",
                color_discrete_map={"교통 환급": "#3B82F6", "사용": "#EF4444"},
                hole=0.4
            )
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=180,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("이용 내역이 존재하지 않습니다.")

    except Exception as e:
        st.error(f"내역을 불러오는 중 오류가 발생했습니다: {e}")

# -----------------------------------------------------------------------------
# 5. 하단 안내문
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("💡 **이용안내**: 본 서비스는 청소년 대중교통 지원사업의 일환으로 제공되며, 적립된 포인트는 제휴된 편의점 및 가맹점에서 현금처럼 사용할 수 있습니다.")
