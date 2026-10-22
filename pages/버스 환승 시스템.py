
import streamlit as st
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="버스 환승 도우미",
    page_icon="🚌",
    layout="centered",
)

KST = ZoneInfo("Asia/Seoul")


def now_kst():
    """한국 표준시를 반환합니다."""
    return datetime.now(KST)


def format_datetime(value):
    return value.strftime("%Y-%m-%d %H:%M:%S")


def init_state():
    if "transfer_records" not in st.session_state:
        st.session_state.transfer_records = []


init_state()

# -----------------------------
# 상단 화면
# -----------------------------
now = now_kst()

st.title("🚌 버스 환승 도우미")
st.caption("현재 시각 확인부터 환승 마감 계산까지")

with st.container(border=True):
    st.subheader("🕒 현재 한국 시각")
    st.markdown(f"## {now.strftime('%H:%M:%S')}")
    st.write(now.strftime("%Y년 %m월 %d일"))
    if st.button("🔄 현재 시각 새로고침", use_container_width=True):
        st.rerun()

st.info(
    "현재 시각은 화면을 새로고침할 때 갱신됩니다. "
    "아래 계산기의 남은 시간도 새로고침 후 다시 계산됩니다."
)

# -----------------------------
# 환승 시간 계산기
# -----------------------------
st.header("⏱️ 환승 시간 계산")

with st.form("transfer_calculator"):
    st.write("첫 번째 버스에서 내린 시각을 입력하세요.")

    col1, col2 = st.columns(2)

    with col1:
        exit_date = st.date_input(
            "하차 날짜",
            value=now.date(),
            key="exit_date",
        )

    with col2:
        exit_time = st.time_input(
            "하차 시각",
            value=now.time().replace(microsecond=0),
            key="exit_time",
        )

    allowed_minutes = st.select_slider(
        "환승 허용 시간(분)",
        options=[10, 15, 20, 30, 40, 60],
        value=30,
    )

    submitted = st.form_submit_button(
        "환승 마감 시간 계산",
        use_container_width=True,
        type="primary",
    )

if submitted:
    try:
        exit_dt = datetime.combine(
            exit_date,
            exit_time,
            tzinfo=KST,
        )
        deadline = exit_dt + timedelta(minutes=allowed_minutes)

        st.session_state.exit_dt = exit_dt
        st.session_state.deadline = deadline
        st.session_state.allowed_minutes = allowed_minutes

    except (ValueError, TypeError, OverflowError):
        st.error("입력한 날짜와 시각을 확인한 뒤 다시 시도하세요.")

# -----------------------------
# 계산 결과
# -----------------------------
if "deadline" in st.session_state:
    exit_dt = st.session_state.exit_dt
    deadline = st.session_state.deadline
    current = now_kst()

    st.subheader("📍 환승 상황")

    with st.container(border=True):
        st.write("첫 번째 버스 하차 시각")
        st.markdown(f"### {exit_dt.strftime('%Y-%m-%d %H:%M')}")

        st.write("환승 마감 시각")
        st.markdown(f"### {deadline.strftime('%Y-%m-%d %H:%M')}")

        remaining_seconds = int((deadline - current).total_seconds())

        if remaining_seconds < 0:
            st.error("⌛ 설정한 환승 시간이 지났습니다.")
            st.write(
                f"마감 시각보다 {abs(remaining_seconds) // 60}분 "
                f"{abs(remaining_seconds) % 60}초 지났습니다."
            )
        elif remaining_seconds == 0:
            st.warning("환승 마감 시각입니다.")
        else:
            remaining_minutes = remaining_seconds // 60
            remaining_secs = remaining_seconds % 60

            if remaining_seconds <= 300:
                st.warning("⚠️ 환승 마감이 5분 이내로 다가왔습니다.")
            else:
                st.success("✅ 설정한 환승 가능 시간 내입니다.")

            st.metric(
                "남은 시간",
                f"{remaining_minutes}분 {remaining_secs}초",
            )

        st.caption(
            "계산 결과는 입력한 허용 시간을 기준으로 하며, "
            "실제 교통카드의 환승 적용을 보장하지 않습니다."
        )

    # -----------------------------
    # 환승 기록
    # -----------------------------
    st.subheader("📝 환승 기록")

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("두 번째 버스 탑승 기록", use_container_width=True):
            boarding_time = now_kst()
            st.session_state.transfer_records.insert(
                0,
                {
                    "기록 시각": boarding_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "최초 하차": exit_dt.strftime("%Y-%m-%d %H:%M"),
                    "환승 마감": deadline.strftime("%Y-%m-%d %H:%M"),
                    "탑승 당시 판정": (
                        "설정 시간 내"
                        if boarding_time <= deadline
                        else "설정 시간 초과"
                    ),
                },
            )
            st.success("두 번째 버스 탑승 시각을 기록했습니다.")

    with col_b:
        if st.button("계산 결과 초기화", use_container_width=True):
            for key in ("exit_dt", "deadline", "allowed_minutes"):
                st.session_state.pop(key, None)
            st.rerun()

    if st.session_state.transfer_records:
        st.dataframe(
            st.session_state.transfer_records,
            use_container_width=True,
            hide_index=True,
        )

        if st.button("전체 기록 삭제"):
            st.session_state.transfer_records = []
            st.rerun()
    else:
        st.caption("아직 기록된 환승 내역이 없습니다.")

# -----------------------------
# 하단 안내
# -----------------------------
st.divider()
st.caption(
    "버스 환승 도우미 · 시간 계산 및 개인 기록 관리용"
)
