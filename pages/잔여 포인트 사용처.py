import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="청소년 교통비 지원 & 포인트 타운",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS 스타일링
st.markdown("""
    <style>
    .main-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .card-box {
        background-color: #F8FAFC;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    .point-highlight {
        font-size: 1.8rem;
        font-weight: 800;
        color: #2563EB;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 세션 상태(Session State) 안정적 초기화
# -----------------------------------------------------------------------------
if "user_points" not in st.session_state:
    st.session_state["user_points"] = 18500  # 기본 보유 포인트

if "monthly_support" not in st.session_state:
    st.session_state["monthly_support"] = 30000  # 월 한도

if "history" not in st.session_state:
    today = datetime.now()
    st.session_state["history"] = [
        {"날짜": (today - timedelta(days=4)).strftime("%Y-%m-%d %H:%M"), "구분": "교통 환급", "상세내용": "시내버스 탑승 (마일리지 적립)", "변동포인트": 500, "잔여포인트": 15500},
        {"날짜": (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), "구분": "사용", "상세내용": "CU 편의점 결제", "변동포인트": -2500, "잔여포인트": 13000},
        {"날짜": (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "구분": "교통 환급", "상세내용": "지하철 1호선 탑승", "변동포인트": 600, "잔여포인트": 13600},
        {"날짜": (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "구분": "사용", "상세내용": "교보문고 모바일권 교환", "변동포인트": -3100, "잔여포인트": 10500},
        {"날짜": today.strftime("%Y-%m-%d %H:%M"), "구분": "교통 환급", "상세내용": "청소년 대중교통 분기 지원금", "변동포인트": 8000, "잔여포인트": 18500},
    ]

# -----------------------------------------------------------------------------
# 3. 상단 헤더 및 메인페이지 이동 버튼
# -----------------------------------------------------------------------------
top_col1, top_col2 = st.columns([1, 4])

with top_col1:
    # 왼쪽 상단 메인으로 돌아가는 버튼
    if st.button("🏠 메인으로", use_container_width=True, help="클릭 시 메인 화면으로 돌아갑니다."):
        st.toast("메인 페이지로 이동했습니다.")
        st.rerun()

with top_col2:
    st.markdown("<div class='main-title'>🚌 청소년 교통비 지원 & 제휴 포인트 타운</div>", unsafe_allow_html=True)

st.divider()

# -----------------------------------------------------------------------------
# 4. PC 화면 3칸 영역 분할 (Layout)
# -----------------------------------------------------------------------------
col1, col2, col3 = st.columns([1, 1.1, 1.2])

# =============================================================================
# [1칸] 교통 포인트 현황
# =============================================================================
with col1:
    st.subheader("📊 1. 포인트 현황")
    
    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.markdown("**홍길동 청소년**님의 현재 잔여 포인트", unsafe_allow_html=True)
    st.markdown(f"<div class='point-highlight'>{st.session_state['user_points']:,} P</div>", unsafe_allow_html=True)
    st.caption("※ 대중교통 이용 시 결제금액의 일부가 자동 적립됩니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    # 이번 달 환급/지원율 프로그레스 바
    used_support = min(st.session_state["user_points"], st.session_state["monthly_support"])
    progress_percent = min(int((used_support / st.session_state["monthly_support"]) * 100), 100)
    
    st.write(f"**이번 달 지원 한도 달성률 ({progress_percent}%)**")
    st.progress(progress_percent / 100)
    st.caption(f"월 최대 지원 한도: {st.session_state['monthly_support']:,}원")

    # 대중교통 이용 적립 시뮬레이션
    st.markdown("---")
    st.markdown("##### 🚌 대중교통 이용 적립 시뮬레이션")
    
    transport_type = st.selectbox(
        "이용 교통수단 선택", 
        ["시내버스 (500P 적립)", "지하철 (600P 적립)", "광역버스 (1,000P 적립)"]
    )
    
    if st.button("교통카드 태그 (적립)", use_container_width=True):
        earned_p = 500
        t_name = "시내버스 탑승"
        if "지하철" in transport_type:
            earned_p = 600
            t_name = "지하철 탑승"
        elif "광역버스" in transport_type:
            earned_p = 1000
            t_name = "광역버스 탑승"
            
        st.session_state["user_points"] += earned_p
        
        # 이용 내역에 추가
        st.session_state["history"].insert(0, {
            "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "구분": "교통 환급",
            "상세내용": f"{t_name} (마일리지 적립)",
            "변동포인트": earned_p,
            "잔여포인트": st.session_state["user_points"]
        })
        st.success(f"{earned_p:,}P가 적립되었습니다!")
        st.rerun()

# =============================================================================
# [2칸] 남은 포인트 사용하기 (제휴 상점)
# =============================================================================
with col2:
    st.subheader("🏪 2. 제휴처 포인트 사용")
    st.caption("적립된 포인트를 편의점, 서점, 카페 쿠폰으로 교환하세요.")

    tab1, tab2, tab3 = st.tabs(["🛍️ 편의점", "📚 서점/문구", "☕ 카페/디저트"])

    items_data = {
        "편의점": [
            {"name": "CU 모바일 3,000원권", "price": 3000, "icon": "🏪"},
            {"name": "GS25 모바일 5,000원권", "price": 5000, "icon": "🏪"},
            {"name": "세븐일레븐 바나나우유", "price": 1700, "icon": "🍌"},
        ],
        "서점/문구": [
            {"name": "문화상품권 5,000원권", "price": 5000, "icon": "📚"},
            {"name": "알라딘 3,000원 할인권", "price": 3000, "icon": "📖"},
            {"name": "스터디플래너 교환권", "price": 4000, "icon": "✏️"},
        ],
        "카페/디저트": [
            {"name": "메가커피 아메리카노", "price": 2000, "icon": "☕"},
            {"name": "빽다방 빽스치노", "price": 3800, "icon": "🥤"},
            {"name": "설빙 5,000원 모바일 쿠폰", "price": 5000, "icon": "🍨"},
        ]
    }

    def render_store(category):
        for idx, item in enumerate(items_data[category]):
            c_a, c_b = st.columns([2.5, 1.5])
            with c_a:
                st.markdown(f"**{item['icon']} {item['name']}**")
                st.markdown(f"<span style='color:#2563EB; font-weight:bold;'>{item['price']:,} P</span>", unsafe_allow_html=True)
            with c_b:
                if st.button("교환", key=f"{category}_{idx}"):
                    if st.session_state["user_points"] >= item['price']:
                        st.session_state["user_points"] -= item['price']
                        st.session_state["history"].insert(0, {
                            "날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "구분": "사용",
                            "상세내용": f"{item['name']} 교환",
                            "변동포인트": -item['price'],
                            "잔여포인트": st.session_state["user_points"]
                        })
                        st.balloons()
                        st.success("교환완료!")
                        st.rerun()
                    else:
                        st.error("포인트 부족")
            st.divider()

    with tab1:
        render_store("편의점")
    with tab2:
        render_store("서점/문구")
    with tab3:
        render_store("카페/디저트")

# =============================================================================
# [3칸] 포인트 사용 내역 및 시각화 차트
# =============================================================================
with col3:
    st.subheader("📜 3. 포인트 이용 내역")
    
    try:
        df = pd.DataFrame(st.session_state["history"])
        
        if not df.empty:
            df_display = df.copy()
            df_display["변동포인트(P)"] = df_display["변동포인트"].apply(
                lambda x: f"+{x:,}" if x > 0 else f"{x:,}"
            )
            df_display["잔여포인트(P)"] = df_display["잔여포인트"].apply(lambda x: f"{x:,}")

            # 이용 내역 표
            st.dataframe(
                df_display[["날짜", "구분", "상세내용", "변동포인트(P)", "잔여포인트(P)"]],
                use_container_width=True,
                hide_index=True,
                height=230
            )

            # 이용 통계 차트 (Plotly)
            st.markdown("##### 📈 이용 비율 통계")
            type_counts = df["구분"].value_counts().reset_index()
            type_counts.columns = ["구분", "건수"]

            fig = px.pie(
                type_counts, 
                values="건수", 
                names="구분", 
                hole=0.4,
                color_discrete_sequence=["#2563EB", "#EF4444"]
            )
            fig.update_layout(
                margin=dict(t=5, b=5, l=5, r=5),
                height=180,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("이용 내역이 없습니다.")

    except Exception as e:
        st.error(f"내역을 불러오는 중 오류가 발생했습니다: {e}")

# -----------------------------------------------------------------------------
# 5. 하단 안내문
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("💡 **이용안내**: 본 서비스는 청소년 대중교통 지원사업의 일환으로 제공되며, 적립된 포인트는 제휴된 편의점 및 가맹점에서 현금처럼 사용할 수 있습니다.")
