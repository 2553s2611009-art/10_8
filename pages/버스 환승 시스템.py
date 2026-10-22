
import streamlit as st
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="버스 환승 도우미",
    page_icon="🚌",
    layout="centered",
)

KST = ZoneInfo("Asia/Seoul")


def current_time():
    return datetime.now(KST)


if "deadline" not in st.session_state:
    st.session_state["deadline"] = None

if "exit_time" not in st.session_state:
    st.session_state["exit_time"] = None

if "records" not in st.session_state:
    st.session_state["records"] = []


now = current_time()

st.title("🚌 버스 환승 도우미")
st.write("현재 시각을 확인하고 환승 마감 시간을 계산하세요.")

st.subheader("🕒 현재 한국 시각")
st.markdown("## " + now.strftime("%H:%M:%S"))
st.write(now.strftime("%Y년 %m월 %d일"))

if st.button("현재 시각 새로고침"):
    st.rerun()

st.divider()
st.subheader("⏱️ 환승 시간 계산")

with st.form("transfer_form"):
    today = current_time()

    selected_date = st.date_input(
        "첫 번째 버스 하차 날짜",
        value=today.date(),
    )

    selected_time = st.time_input(
        "첫 번째 버스 하차 시각",
        value=today.time().replace(tzinfo=None, microsecond=0),
    )

    allowed_minutes = st.selectbox(
        "환승 허용 시간",
        [10, 15, 20, 30, 40, 60],
        index=3,
    )

    calculate = st.form_submit_button("환승 시간 계산")

if calculate:
    try:
        exit_dt = datetime.combine(selected_date, selected_time)
        deadline = exit_dt + timedelta(minutes=allowed_minutes)

        st.session_state["exit_time"] = exit_dt
        st.session_state["deadline"] = deadline

    except (ValueError, TypeError, OverflowError):
        st.error("날짜와 시각을 다시 확인해 주세요.")

if st.session_state["deadline"] is not None:
    exit_dt = st.session_state["exit_time"]
    deadline = st.session_state["deadline"]
    now = current_time()

    st.divider()
    st.subheader("📍 계산 결과")

    st.write("하차 시각:", exit_dt.strftime("%Y-%m-%d %H:%M"))
    st.write("환승 마감:", deadline.strftime("%Y-%m-%d %H:%M"))

    # 입력한 날짜와 시각을 한국 시각으로 비교합니다.
    exit_kst = exit_dt.replace(tzinfo=KST)
    deadline_kst = deadline.replace(tzinfo=KST)

    seconds_left = int((deadline_kst - now).total_seconds())

    if seconds_left < 0:
        st.error("설정한 환승 시간이 지났습니다.")
    elif seconds_left == 0:
        st.warning("환승 마감 시각입니다.")
    else:
        minutes_left = seconds_left // 60
        seconds = seconds_left % 60

        st.metric(
            "남은 시간",
            f"{minutes_left}분 {seconds}초",
        )

        if seconds_left <= 300:
            st.warning("환승 마감까지 5분 이내입니다.")
        else:
            st.success("설정한 환승 시간 내입니다.")

    if st.button("지금 탑승 기록 저장"):
        record_time = current_time()

        st.session_state["records"].insert(
            0,
            {
                "기록 시각": record_time.strftime("%Y-%m-%d %H:%M:%S"),
                "하차 시각": exit_dt.strftime("%Y-%m-%d %H:%M"),
                "환승 마감": deadline.strftime("%Y-%m-%d %H:%M"),
                "설정 시간 기준": (
                    "시간 내"
                    if record_time <= deadline_kst
                    else "시간 초과"
                ),
            },
        )
        st.success("탑승 기록을 저장했습니다.")

    if st.session_state["records"]:
        st.subheader("📋 탑승 기록")
        st.dataframe(
            st.session_state["records"],
            use_container_width=True,
            hide_index=True,
        )

        if st.button("기록 전체 삭제"):
            st.session_state["records"] = []
            st.rerun()

    if st.button("계산 초기화"):
        st.session_state["deadline"] = None
        st.session_state["exit_time"] = None
        st.rerun()

st.divider()
st.caption("실제 교통카드 환승 판정이 아닌 시간 계산용 앱입니다.")
st.caption("기록은 앱 세션 동안만 유지됩니다.")
