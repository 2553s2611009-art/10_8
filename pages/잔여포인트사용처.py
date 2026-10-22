import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 기본 설정 (와이드 모드로 설정하여 PC에서 3열이 한눈에 보이게 함)
st.set_page_config(
    page_title="학생 교통포인트 지원 시스템",
    page_icon="🚌",
    layout="wide"
)

# 2. 세션 상태(Session State) 초기화 - 데이터 유지 목적
if "balance" not in st.session_state:
    st.session_state.balance = 45000  # 기본 잔여 포인트 (예: 총 50,000 중 5,000원 사용 상태)

if "total_allocated" not in st.session_state:
    st.session_state.total_allocated = 50000  # 이번 달 총 지원 포인트

if "history" not in st.session_state:
    # 기본 거래 내역 예시
    st.session_state.history = [
        {"시각": "2026-10-18 08:30", "구분": "교통", "사용처": "시내버스", "금액": 1500, "잔액": 48500},
        {"시각": "2026-10-18 18:15", "구분": "교통", "사용처": "지하철", "금액": 1400, "잔액": 47100},
        {"시각": "2026-10-19 12:10", "구분": "제휴처", "사용처": "GS25 편의점", "금액": 2100, "잔액": 45000},
    ]

# 3. 추가 요청사항: 왼쪽 상단 메인페이지 이동 버튼 (사이드바 최상단)
with st.sidebar:
    st.title("📌 Navigation")
    if st.button("🏠 메인페이지로 돌아가기", use_container_width=True):
        # Streamlit의 쿼리 파라미터를 리셋하거나 페이지를 새로고침하는 효과
        st.rerun()
    st.divider()
    st.write("**학생 정보**")
    st.info("👤 홍길동 (대구대학교 2학년)\n\n💳 카드번호: 1004-9921-8812")

# 앱 타이틀
st.title("🚌 학생 교통포인트 지원 & 사용 센터")
st.caption("청소년 및 대학생을 위한 월별 교통 지원금 및 제휴처 포인트 관리 시스템")
st.write("")

# 4. 핵심 레이아웃: PC 화면 기준 3개 열(Column) 구성
col1, col2, col3 = st.columns([1, 1, 1.2])

# -------------------------------------------------------------------
# [칸 1] 전체 교통포인트 현황
# -------------------------------------------------------------------
with col1:
    st.subheader("📊 포인트 현황")
    
    used_points = st.session_state.total_allocated - st.session_state.balance
    usage_rate = (used_points / st.session_state.total_allocated) * 100

    # 주요 지표 (Metrics)
    st.metric(label="이번 달 총 지원금", value=f"{st.session_state.total_allocated:,} P")
    st.metric(
        label="현재 잔여 포인트", 
        value=f"{st.session_state.balance:,} P", 
        delta=f"-{used_points:,} P (사용됨)",
        delta_color="normal"
    )

    # 사용률 프로그레스 바
    st.write(f"**포인트 소진율 ({usage_rate:.1f}%)**")
    st.progress(usage_rate / 100)

    st.info("💡 **알림**: 매월 1일 50,000P가 자동 충전되며, 이월되지 않고 소멸됩니다.")


# -------------------------------------------------------------------
# [칸 2] 잔여 포인트 사용하기 (제휴 편의점 및 교통 결제)
# -------------------------------------------------------------------
with col2:
    st.subheader("🛒 포인트 사용하기")
    
    with st.form(key="use_point_form", clear_on_submit=True):
        category = st.selectbox(
            "사용 구분",
            ["편의점/제휴처", "대중교통 (일반)", "기타 제휴 서비스"]
        )
        
        place_options = {
            "편의점/제휴처": ["GS25", "CU", "세븐일레븐", "이마트24", "대학 내 학식당"],
            "대중교통 (일반)": ["시내버스", "지하철", "마을버스"],
            "기타 제휴 서비스": ["따릉이/공유킥보드", "알라딘 중고서점"]
        }
        
        place = st.selectbox("사용처 선택", place_options[category])
        amount = st.number_input("사용 금액 (P)", min_value=100, step=100, value=1000)
        
        submit_button = st.form_submit_button(label="결제 요청", use_container_width=True)

    # 결제 처리 logic (예외 처리 포함)
    if submit_button:
        try:
            amount = int(amount)
            if amount <= 0:
                st.error("100원 이상의 금액을 입력해주세요.")
            elif amount > st.session_state.balance:
                st.error(f"잔액이 부족합니다! (현재 잔액: {st.session_state.balance:,} P)")
            else:
                # 포인트 차감
                st.session_state.balance -= amount
                
                # 내역 추가
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.history.insert(0, {
                    "시각": now_str,
                    "구분": category.split()[0],
                    "사용처": place,
                    "금액": amount,
                    "잔액": st.session_state.balance
                })
                
                st.success(f"✅ {place}에서 {amount:,} P 결제 완료!")
                st.rerun()  # 화면 즉시 갱신
        except Exception as e:
            st.error(f"결제 중 오류가 발생했습니다: {e}")


# -------------------------------------------------------------------
# [칸 3] 포인트 사용 내역
# -------------------------------------------------------------------
with col3:
    st.subheader("📜 사용 내역")

    if st.session_state.history:
        # 데이터프레임 변환
        df = pd.DataFrame(st.session_state.history)
        
        # 보기 좋게 표로 출력
        st.dataframe(
            df,
            column_config={
                "시각": st.column_config.TextColumn("일시"),
                "구분": st.column_config.TextColumn("분류"),
                "사용처": st.column_config.TextColumn("사용처"),
                "금액": st.column_config.NumberColumn("사용 금액", format="%d P"),
                "잔액": st.column_config.NumberColumn("남은 잔액", format="%d P"),
            },
            hide_index=True,
            use_container_width=True,
            height=300
        )
        
        # 내역 초기화 기능 (테스트용)
        if st.button("내역 초기화 (테스트용)", use_container_width=True):
            st.session_state.balance = 50000
            st.session_state.history = []
            st.rerun()
    else:
        st.write("최근 사용 내역이 없습니다.")
