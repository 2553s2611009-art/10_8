import streamlit as st
from datetime import datetime, date, time, timedelta

st.set_page_config(
    page_title="버스 환승 시간 계산기",
    page_icon="🚌",
    layout="centered",
)

# -----------------------------
# 기본 스타일
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {
        max-width: 820px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.5rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #123B35, #237A62);
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero h1 {
        color: white;
        margin-bottom: 0.5rem;
    }
    .hero p {
        color: #E4F4EF;
        margin-bottom: 0;
    }
    .result {
        padding: 1.2rem;
        border: 1px solid #D9E5E0;
        border-radius: 14px;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 제목
# -----------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🚌 버스 환승 시간 계산기</h1>
        <p>다음 버스, 아직 탈 수 있을까?<br>
        하차 시각과 탑승 예정 시각으로 환승 시간을 확인하세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("시간을 입력하면 환승 제한 시간까지 얼마나 남았는지 계산합니다.")

# -----------------------------
# 입력 영역
# -----------------------------
st.subheader("📍 이동 정보")

today = date.today()

with st.form("transfer_form"):
    col1, col2 = st.columns(2)

    with col1:
        get_off_time = st.time_input(
            "첫 버스 하차 시각",
            value=time(9, 0),
            step=timedelta(minutes=1),
            help="첫 번째 버스에서 내린 시각을 입력하세요.",
        )

    with col2:
        next_bus_time = st.time_input(
            "다음 버스 탑승 예정 시각",
            value=time(9, 15),
            step=timedelta(minutes=1),
            help="다음 버스에 탈 예정인 시각을 입력하세요.",
        )

    limit_minutes = st.slider(
        "환승 제한 시간 (분)",
        min_value=10,
        max_value=120,
        value=30,
        step=5,
        help="지역과 교통카드 정책에 맞는 제한 시간을 설정하세요.",
    )

    submitted = st.form_submit_button(
        "환승 시간 계산하기",
        type="primary",
        use_container_width=True,
    )

# -----------------------------
# 계산 및 결과
# -----------------------------
if submitted:
    try:
        departure = datetime.combine(today, get_off_time)
        next_bus = datetime.combine(today, next_bus_time)

        # 다음 날 탑승하는 경우 처리
        if next_bus < departure:
            next_bus += timedelta(days=1)

        elapsed = int((next_bus - departure).total_seconds() // 60)
        remaining = limit_minutes - elapsed

        st.divider()
        st.subheader("📊 계산 결과")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "경과 시간",
            f"{elapsed}분",
        )
        col2.metric(
            "환승 제한",
            f"{limit_minutes}분",
        )
        col3.metric(
            "남은 시간",
            f"{remaining}분" if remaining >= 0 else f"{abs(remaining)}분 초과",
        )

        if elapsed == 0:
            st.info(
                "두 시각이 같습니다. 실제 이동 및 승하차에 걸리는 시간도 고려하세요."
            )

        if remaining > 10:
            st.success(
                f"환승 제한 시간까지 {remaining}분 남았습니다. "
                "다음 버스의 도착 정보를 확인하고 여유 있게 이동하세요."
            )
        elif remaining > 0:
            st.warning(
                f"환승 제한 시간까지 {remaining}분 남았습니다. "
                "서둘러 이동하고 실제 환승 조건을 확인하세요."
            )
        elif remaining == 0:
            st.warning(
                "설정한 환승 제한 시간에 도달했습니다. "
                "실제 환승 인정 여부는 교통카드 정책을 확인하세요."
            )
        else:
            st.error(
                f"설정한 제한 시간을 {abs(remaining)}분 초과했습니다. "
                "환승 할인이 인정되지 않을 수 있습니다."
            )

        # 시간 흐름 시각화
        st.markdown("### ⏱️ 시간 사용 현황")

        if elapsed <= limit_minutes:
            progress = elapsed / limit_minutes
            st.progress(min(max(progress, 0.0), 1.0))
            st.caption(
                f"제한 시간 {limit_minutes}분 중 {elapsed}분이 경과했습니다."
            )
        else:
            st.progress(1.0)
            st.caption(
                f"제한 시간을 {elapsed - limit_minutes}분 초과했습니다."
            )

        # 계산 상세 정보
        with st.expander("계산 상세 정보"):
            st.write(f"- 첫 버스 하차: {departure.strftime('%H:%M')}")
            st.write(f"- 다음 버스 탑승: {next_bus.strftime('%Y-%m-%d %H:%M')}")
            st.write(f"- 경과 시간: {elapsed}분")
            st.write(f"- 설정한 제한 시간: {limit_minutes}분")

        st.info(
            "이 결과는 입력한 시각과 설정한 제한 시간에 따른 단순 계산입니다. "
            "실제 환승 할인은 지역, 노선, 교통카드, 환승 횟수, "
            "시간대 등 적용 규정에 따라 달라질 수 있습니다."
        )

    except (TypeError, ValueError, OverflowError):
        st.error(
            "시간을 계산할 수 없습니다. 입력한 시간을 확인하고 다시 시도하세요."
        )
    except Exception:
        st.error(
            "계산 중 예상하지 못한 오류가 발생했습니다. "
            "입력값을 확인한 뒤 다시 시도하세요."
        )

else:
    st.markdown(
        """
        <div class="result">
            <h4>💡 사용 방법</h4>
            1. 첫 버스에서 내린 시각을 입력하세요.<br>
            2. 다음 버스에 탈 예정인 시각을 입력하세요.<br>
            3. 적용할 환승 제한 시간을 선택하세요.<br>
            4. 계산 버튼을 누르면 남은 시간과 결과를 확인할 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# 하단 안내
# -----------------------------
st.divider()
st.caption(
    "🚌 Bus Transfer Timer | 시간 계산 참고용 서비스 · "
    "실제 환승 할인 보장 서비스가 아닙니다."
)
