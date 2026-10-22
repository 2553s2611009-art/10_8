
import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# =====================================
# 1. 기본 설정
# =====================================
st.set_page_config(
    page_title="버스 환승 도우미",
    page_icon="🚌",
    layout="centered",
)

KST = ZoneInfo("Asia/Seoul")


def get_now():
    """현재 한국 시각을 반환합니다."""
    return datetime.now(KST)


def init_state():
    """세션 상태를 안전하게 초기화합니다."""
    if "transfer_records" not in st.session_state:
        st.session_state["transfer_records"] = []

    if "exit_dt" not in st.session_state:
        st.session_state["exit_dt"] = None

    if "deadline" not in st.session_state:
        st.session_state["deadline"] = None


init_state()

# =====================================
# 2. 제목 및 현재 시각
# =====================================
now = get_now()

st.title("🚌 버스 환승 도우미")
st.caption("환승 시간 계산부터 탑승 기록까지")

with st.container(border=True):
    st.subheader("🕒 현재 한국 시각")
    st.markdown(f"## {now.strftime('%H:%M:%S')}")
    st.write(now.strftime("%Y년 %m월 %d일"))

    if st.button("🔄 현재 시각 갱신", use_container_width=True):
        st.rerun()

st.caption("현재 시각과 남은 시간은 화면을 갱신할 때 업데이트됩니다.")

st.divider()

# =====================================
# 3. 환승 시간 계산
# =====================================
st.header("⏱️ 환승 시간 계산기")

with st.form("transfer_form"):
    st.write("첫 번째 버스에서 내린 날짜와 시각을 입력하세요.")

    current = get_now()
    col1, col2 = st.columns(2)

    with col1:
        exit_date = st.date_input(
            "하차 날짜",
            value=current.date(),
            key="exit_date_input",
        )

    with col2:
        exit_time = st.time_input(
            "하차 시각",
            value=current.time().replace(
                tzinfo=None,
                microsecond=0,
            ),
            key="exit_time_input",
        )

    allowed_minutes = st.selectbox(
        "환승 허용 시간",
        options=[10, 15, 20, 30, 40, 60],
        index=3,
        format_func=lambda x: f"{x}분",
    )

    calculate = st.form_submit_button(
        "환승 마감 시간 계산하기",
        use_container_width=True,
        type="primary",
    )

if calculate:
    try:
        # Streamlit에서 입력받은 시각은 시간대 정보가 없는
        # datetime으로 변환한 후 한국 시간대를 지정합니다.
        naive_exit = datetime.combine(
            exit_date,
            exit_time.replace(tzinfo=None),
        )
        exit_dt = naive_exit.replace(tzinfo=KST)

        deadline = exit_dt + timedelta(minutes=int(allowed_minutes))

        st.session_state["exit_dt"] = exit_dt
        st.session_state["deadline"] = deadline
        st.session_state["allowed_minutes"] = int(allowed_minutes)

    except (ValueError, TypeError, OverflowError):
        st.error("날짜 또는 시각을 확인한 후 다시 시도해 주세요.")

# =====================================
# 4. 계산 결과와 남은 시간
# =====================================
exit_dt = st.session_state["exit_dt"]
deadline = st.session_state["deadline"]

if exit_dt is not None and deadline is not None:
    current = get_now()

    st.subheader("📍 환승 상황판")

    with st.container(border=True):
        st.write("첫 번째 버스 하차 시각")
        st.markdown(f"### {exit_dt.strftime('%Y-%m-%d %H:%M')}")

        st.write("환승 마감 시각")
        st.markdown(f"### {deadline.strftime('%Y-%m-%d %H:%M')}")

        remaining = int((deadline - current).total_seconds())

        if remaining < 0:
            st.error("⌛ 설정한 환승 시간이 지났습니다.")
            elapsed = abs(remaining)
            st.write(
                f"마감 시각으로부터 "
                f"{elapsed // 60}분 {elapsed % 60}초 경과"
            )

        elif remaining == 0:
            st.warning("환승 마감 시각입니다.")

        else:
            minutes = remaining // 60
            seconds = remaining % 60

            st.metric(
                "환승 마감까지 남은 시간",
                f"{minutes}분 {seconds}초",
            )

            if remaining <= 300:
                st.warning("⚠️ 환승 마감이 5분 이내입니다.")
            else:
                st.success("✅ 설정한 환승 시간 안에 있습니다.")

    st.caption(
        "이 결과는 직접 설정한 시간에 따른 계산입니다. "
        "실제 교통카드의 환승 인정 여부와 다를 수 있습니다."
    )

    # =====================================
    # 5. 탑승 기록
    # =====================================
    st.subheader("📝 두 번째 버스 탑승 기록")

    if st.button(
        "🚌 지금 탑승한 것으로 기록",
        use_container_width=True,
    ):
        boarding_time = get_now()

        record = {
            "탑승 기록 시각": boarding_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "첫 버스 하차": exit_dt.strftime("%Y-%m-%d %H:%M"),
            "환승 마감": deadline.strftime("%Y-%m-%d %H:%M"),
            "설정 시간 기준": (
                "시간 내"
                if boarding_time <= deadline
                else "시간 초과"
            ),
        }

        st.session_state["transfer_records"].insert(0, record)
        st.success("탑승 기록을 저장했습니다.")

    st.divider()

    # =====================================
    # 6. 기록 목록
    # =====================================
    st.subheader("📋 환승 기록 목록")

    records = st.session_state["transfer_records"]

    if records:
        st.dataframe(
            records,
            use_container_width=True,
            hide_index=True,
        )

        if st.button("전체 환승 기록 삭제"):
            st.session_state["transfer_records"] = []
            st.rerun()
    else:
        st.info("아직 저장된 환승 기록이 없습니다.")

    if st.button("계산 결과 초기화"):
        st.session_state["exit_dt"] = None
        st.session_state["deadline"] = None
        st.rerun()

else:
    st.info("하차 시각을 입력하고 계산 버튼을 눌러 주세요.")

# =====================================
# 7. 하단 안내
# =====================================
st.divider()
st.caption("버스 환승 도우미 | 한국 표준시 기준")
st.caption("환승 기록은 현재 앱 세션에 저장되며 영구 보관되지 않습니다.")
