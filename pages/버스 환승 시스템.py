
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


# 세션 데이터 초기화
if "balance" not in st.session_state:
    st.session_state.balance = 10000

if "deadline" not in st.session_state:
    st.session_state.deadline = None

if "exit_time" not in st.session_state:
    st.session_state.exit_time = None

if "records" not in st.session_state:
    st.session_state.records = []

# 제목
st.title("🚌 버스 환승 도우미")
st.caption("잔액 관리 · 환승 시간 계산")

# 현재 시각
now = current_time()

with st.container(border=True):
    st.subheader("🕒 현재 한국 시각")
    st.markdown(f"## {now.strftime('%H:%M:%S')}")
    st.write(now.strftime("%Y년 %m월 %d일"))

    if st.button("🔄 시각 새로고침"):
        st.rerun()

# 교통카드 잔액
st.divider()
st.subheader("💳 교통카드 잔액")

st.metric(
    label="현재 잔액",
    value=f"{st.session_state.balance:,}원",
)

with st.expander("잔액 충전하기"):
    with st.form("charge_form"):
        charge_amount = st.number_input(
            "충전 금액 (원)",
            min_value=1000,
            max_value=100000,
            value=10000,
            step=1000,
        )
        charge_submit = st.form_submit_button("충전하기")

    if charge_submit:
        st.session_state.balance += int(charge_amount)
        st.success(f"{charge_amount:,}원을 충전했습니다.")
        st.rerun()

with st.expander("버스 요금 차감하기"):
    with st.form("fare_form"):
        fare = st.number_input(
            "버스 요금 (원)",
            min_value=0,
            max_value=10000,
            value=1500,
            step=100,
        )
        fare_submit = st.form_submit_button("요금 차감")

    if fare_submit:
        if fare > st.session_state.balance:
            st.error("잔액이 부족합니다.")
        else:
            st.session_state.balance -= int(fare)
            st.success(f"{fare:,}원이 차감되었습니다.")
            st.rerun()

# 환승 계산
st.divider()
st.subheader("⏱️ 환승 시간 계산")

with st.form("transfer_form"):
    now = current_time()

    selected_date = st.date_input(
        "첫 번째 버스 하차 날짜",
        value=now.date(),
    )

    selected_time = st.time_input(
        "첫 번째 버스 하차 시각",
        value=now.time().replace(tzinfo=None, microsecond=0),
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
        deadline = exit_dt + timedelta(minutes=int(allowed_minutes))

        st.session_state.exit_time = exit_dt
        st.session_state.deadline = deadline

    except (ValueError, TypeError, OverflowError):
        st.error("날짜와 시각을 다시 확인해 주세요.")

if st.session_state.deadline is not None:
    exit_dt = st.session_state.exit_time
    deadline = st.session_state.deadline
    deadline_kst = deadline.replace(tzinfo=KST)

    st.write("하차 시각:", exit_dt.strftime("%Y-%m-%d %H:%M"))
    st.write("환승 마감:", deadline.strftime("%Y-%m-%d %H:%M"))

    seconds_left = int(
        (deadline_kst - current_time()).total_seconds()
    )

    if seconds_left < 0:
        st.error("설정한 환승 시간이 지났습니다.")
    elif seconds_left == 0:
        st.warning("환승 마감 시각입니다.")
    else:
        minutes_left = seconds_left // 60
        seconds = seconds_left % 60

        st.metric("환승 마감까지 남은 시간",
                  f"{minutes_left}분 {seconds}초")

        if seconds_left <= 300:
            st.warning("환승 마감까지 5분 이내입니다.")
        else:
            st.success("설정한 환승 시간 내입니다.")

# 안내
st.divider()
st.caption("잔액은 앱에서 직접 관리하는 모의 잔액입니다.")
st.caption("실제 교통카드 잔액 및 요금과 연동되지 않습니다.")
st.caption("앱 세션이 종료되면 잔액이 초기화될 수 있습니다.")
