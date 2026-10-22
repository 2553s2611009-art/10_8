import csv
import io
from datetime import date, datetime

import streamlit as st

st.set_page_config(page_title="교통 포인트", page_icon="🚌", layout="wide")

# 예시 기준이며 실제 교통카드·택시 결제 또는 공공 포인트 제도와 연동되지 않습니다.
EARN_RULES = {
    "버스 이용": {"points": 120, "icon": "🚌", "description": "버스 이용 1회당"},
    "택시 이용": {"points": 300, "icon": "🚕", "description": "택시 이용 1회당"},
}
REDEEM_OPTIONS = {
    "버스 교통비 할인": {"cost": 500, "discount": "500원 할인 (모의 처리)", "icon": "🚌"},
    "택시 교통비 할인": {"cost": 1000, "discount": "1,000원 할인 (모의 처리)", "icon": "🚕"},
}

if "opening_balance" not in st.session_state:
    # 샘플 내역을 포함해 첫 화면 잔액이 예시 화면처럼 보이도록 설정
    st.session_state.opening_balance = 12430
if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {
            "id": "sample-1", "date": date(2026, 9, 1), "kind": "적립",
            "activity": "버스 이용", "points": 120, "note": "예시 기록"
        },
        {
            "id": "sample-2", "date": date(2026, 9, 8), "kind": "적립",
            "activity": "택시 이용", "points": 300, "note": "예시 기록"
        },
        {
            "id": "sample-3", "date": date(2026, 9, 3), "kind": "사용",
            "activity": "교통비 할인 (버스)", "points": -500, "note": "예시 기록"
        },
    ]
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "show_all_earn" not in st.session_state:
    st.session_state.show_all_earn = False
if "show_all_use" not in st.session_state:
    st.session_state.show_all_use = False

def balance():
    return int(st.session_state.opening_balance) + sum(
        int(item["points"]) for item in st.session_state.transactions
    )

def add_transaction(kind, activity, points, note=""):
    st.session_state.transactions.append({
        "id": f"{datetime.now().timestamp()}-{len(st.session_state.transactions)}",
        "date": date.today(),
        "kind": kind,
        "activity": activity,
        "points": int(points),
        "note": note,
    })

st.markdown("""
<style>
.stApp {background: #f7f9fc;}
.block-container {max-width: 1100px; padding-top: 1.5rem; padding-bottom: 3rem;}
.brand {font-size: 2.25rem; font-weight: 800; color: #12294b; margin-bottom: .15rem;}
.subbrand {color: #64748b; margin-bottom: 1.3rem;}
.point-card {
    background: linear-gradient(135deg, #65c5ff 0%, #1688f5 55%, #0860c9 100%);
    color: white; border-radius: 18px; padding: 1.5rem 1.6rem;
    box-shadow: 0 5px 14px #153e7a25; min-height: 180px;
}
.point-label {font-size: 1.15rem; font-weight: 700; opacity: .96;}
.point-number {font-size: clamp(2.4rem, 6vw, 4.1rem); font-weight: 850; line-height: 1.25; margin: .45rem 0;}
.point-foot {font-size: .9rem; opacity: .92;}
.action-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 16px;
    padding: 1rem; min-height: 130px; box-shadow: 0 3px 10px #1e293b0a;
}
.action-icon {font-size: 2.2rem;}
.action-title {font-size: 1.15rem; font-weight: 750; color: #173b6c;}
.section-title {font-size: 1.35rem; font-weight: 800; color: #182b49; margin: .6rem 0;}
.tx {
    background: white; border: 1px solid #e5eaf2; border-radius: 12px;
    padding: .75rem .9rem; margin-bottom: .5rem;
}
.small-muted {color: #778399; font-size: .85rem;}
</style>
""", unsafe_allow_html=True)

# Header
head1, head2, head3 = st.columns([5, 1, 1])
with head1:
    st.markdown('<div class="brand">🚌 교통 포인트</div><div class="subbrand">이동할수록 쌓이는 나의 포인트</div>', unsafe_allow_html=True)
with head2:
    if st.button("🔔 알림", use_container_width=True):
        st.session_state.notifications.append(f"{datetime.now().strftime('%H:%M')} · 알림을 확인했어요.")
        st.session_state.open_notifications = not st.session_state.get("open_notifications", False)
with head3:
    if st.button("☰ 메뉴", use_container_width=True):
        st.session_state.open_menu = not st.session_state.get("open_menu", False)

if st.session_state.get("open_notifications", False):
    with st.container(border=True):
        st.markdown("#### 🔔 알림")
        if st.session_state.notifications:
            for n in reversed(st.session_state.notifications[-5:]):
                st.write("• " + n)
        else:
            st.info("새로운 알림이 없습니다.")
if st.session_state.get("open_menu", False):
    with st.container(border=True):
        st.markdown("#### 메뉴")
        st.write("• 내 포인트")
        st.write("• 버스·택시 이용하기")
        st.write("• 교통비 할인")
        st.write("• 적립 및 사용 내역")
        st.caption("이 메뉴는 현재 페이지의 주요 기능 안내입니다.")

st.caption("※ 예시 포인트로 동작하는 데모입니다. 실제 교통카드·택시 결제 및 현금 할인과 연결되지 않습니다.")

# Balance hero
current_balance = balance()
earn_total = sum(max(0, int(x["points"])) for x in st.session_state.transactions)
used_total = sum(abs(min(0, int(x["points"]))) for x in st.session_state.transactions)

st.markdown(f"""
<div class="point-card">
  <div class="point-label">🪙 내 포인트</div>
  <div class="point-number">{current_balance:,} 원</div>
  <div class="point-foot">누적 적립 {earn_total:,} P　 ·　 누적 사용 {used_total:,} P</div>
  <div style="font-size:2rem; text-align:right; margin-top:-.7rem">🚌 🚕</div>
</div>
""", unsafe_allow_html=True)

st.write("")
st.markdown('<div class="section-title">🚍 교통 포인트 모으기</div>', unsafe_allow_html=True)
bus_col, taxi_col = st.columns(2, gap="medium")

with bus_col:
    st.markdown('<div class="action-card"><div class="action-icon">🚌</div><div class="action-title">버스 이용하기</div><div class="small-muted">이용 기록 1회당 +120 P</div></div>', unsafe_allow_html=True)
    with st.form("bus_form"):
        bus_date = st.date_input("버스 이용 날짜", value=date.today(), max_value=date.today(), key="bus_date")
        bus_note = st.text_input("메모 (선택)", placeholder="예: 등교할 때 이용", key="bus_note")
        bus_submit = st.form_submit_button("버스 포인트 적립", use_container_width=True)
        if bus_submit:
            add_transaction("적립", "버스 이용", EARN_RULES["버스 이용"]["points"], bus_note.strip())
            st.session_state.notifications.append(f"{date.today().isoformat()} · 버스 이용 +120 P 적립")
            # 날짜 입력값을 거래에 반영
            st.session_state.transactions[-1]["date"] = bus_date
            st.success("버스 이용 포인트 120 P를 적립했어요!")
            st.rerun()

with taxi_col:
    st.markdown('<div class="action-card"><div class="action-icon">🚕</div><div class="action-title">택시 이용하기</div><div class="small-muted">이용 기록 1회당 +300 P</div></div>', unsafe_allow_html=True)
    with st.form("taxi_form"):
        taxi_date = st.date_input("택시 이용 날짜", value=date.today(), max_value=date.today(), key="taxi_date")
        taxi_note = st.text_input("메모 (선택)", placeholder="예: 귀가할 때 이용", key="taxi_note")
        taxi_submit = st.form_submit_button("택시 포인트 적립", use_container_width=True)
        if taxi_submit:
            add_transaction("적립", "택시 이용", EARN_RULES["택시 이용"]["points"], taxi_note.strip())
            st.session_state.notifications.append(f"{date.today().isoformat()} · 택시 이용 +300 P 적립")
            st.session_state.transactions[-1]["date"] = taxi_date
            st.success("택시 이용 포인트 300 P를 적립했어요!")
            st.rerun()

st.write("")
st.markdown('<div class="section-title">🪙 포인트로 교통비 할인받기</div>', unsafe_allow_html=True)
st.caption("아래 할인은 앱 내부에서 포인트 사용을 연습하는 기능이며 실제 할인 쿠폰은 발급되지 않습니다.")
redemption_cols = st.columns(2)
for idx, (name, option) in enumerate(REDEEM_OPTIONS.items()):
    with redemption_cols[idx]:
        with st.container(border=True):
            st.markdown(f"### {option['icon']} {name}")
            st.write(f"필요 포인트: **{option['cost']:,} P**")
            st.write(option["discount"])
            if st.button(f"{option['cost']:,} P 사용하기", key=f"redeem_{idx}", use_container_width=True, disabled=current_balance < option["cost"]):
                add_transaction("사용", f"교통비 할인 ({'버스' if idx == 0 else '택시'})", -option["cost"], "앱 내 모의 할인")
                st.session_state.notifications.append(f"{date.today().isoformat()} · {name} 신청: -{option['cost']:,} P")
                st.success("포인트 사용을 기록했어요.")
                st.rerun()
if current_balance < min(x["cost"] for x in REDEEM_OPTIONS.values()):
    st.info("할인 기능을 이용하려면 포인트를 더 적립해 주세요.")

st.write("")
st.markdown('<div class="section-title">📋 최근 적립 내역</div>', unsafe_allow_html=True)
earn_records = sorted([x for x in st.session_state.transactions if int(x["points"]) > 0], key=lambda x: (x["date"], x["id"]), reverse=True)
if not st.session_state.show_all_earn:
    earn_records = earn_records[:3]
if not earn_records:
    st.info("아직 적립 내역이 없어요. 버스나 택시 이용을 기록해 보세요.")
else:
    for item in earn_records:
        icon = "🚌" if "버스" in item["activity"] else "🚕" if "택시" in item["activity"] else "🪙"
        st.markdown(f"""
        <div class="tx">
          <div style="display:flex;align-items:center;gap:12px">
            <div style="font-size:2rem">{icon}</div>
            <div style="flex:1"><b>{item['activity']}</b><div class="small-muted">{item['date'].isoformat()} {('· ' + item['note']) if item['note'] else ''}</div></div>
            <div style="font-size:1.25rem;font-weight:800;color:#167a45">+ {int(item['points']):,} P</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
if len([x for x in st.session_state.transactions if int(x["points"]) > 0]) > 3:
    if st.button("적립 내역 전체보기" if not st.session_state.show_all_earn else "최근 내역만 보기", key="toggle_earn"):
        st.session_state.show_all_earn = not st.session_state.show_all_earn
        st.rerun()

st.markdown('<div class="section-title">🧾 포인트 사용 내역</div>', unsafe_allow_html=True)
use_records = sorted([x for x in st.session_state.transactions if int(x["points"]) < 0], key=lambda x: (x["date"], x["id"]), reverse=True)
if not st.session_state.show_all_use:
    use_records = use_records[:3]
if not use_records:
    st.info("아직 포인트 사용 내역이 없어요.")
else:
    for item in use_records:
        icon = "🚌" if "버스" in item["activity"] else "🚕"
        st.markdown(f"""
        <div class="tx">
          <div style="display:flex;align-items:center;gap:12px">
            <div style="font-size:2rem">{icon}</div>
            <div style="flex:1"><b>{item['activity']}</b><div class="small-muted">{item['date'].isoformat()} · {item['note']}</div></div>
            <div style="font-size:1.25rem;font-weight:800;color:#b45309">− {abs(int(item['points'])):,} P</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
if len([x for x in st.session_state.transactions if int(x["points"]) < 0]) > 3:
    if st.button("사용 내역 전체보기" if not st.session_state.show_all_use else "최근 내역만 보기", key="toggle_use"):
        st.session_state.show_all_use = not st.session_state.show_all_use
        st.rerun()

st.write("")
with st.expander("📚 전체 거래 내역 및 CSV 다운로드"):
    all_records = sorted(st.session_state.transactions, key=lambda x: (x["date"], x["id"]), reverse=True)
    if all_records:
        for item in all_records:
            sign = "+" if item["points"] > 0 else "−"
            st.write(f"{item['date'].isoformat()} · {item['activity']} · {sign}{abs(int(item['points'])):,} P")
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["날짜", "유형", "활동", "포인트", "메모"])
        for item in sorted(all_records, key=lambda x: (x["date"], x["id"])):
            writer.writerow([item["date"].isoformat(), item["kind"], item["activity"], item["points"], item["note"]])
        st.download_button("전체 내역 CSV 다운로드", data=("\ufeff" + buffer.getvalue()).encode("utf-8"), file_name="traffic_points_history.csv", mime="text/csv")
        st.caption("예시 기록은 화면 구성을 보여주기 위해 포함되어 있습니다.")
    else:
        st.info("거래 내역이 없습니다.")

st.divider()
st.caption("저장 안내: 기록은 현재 Streamlit 세션에 저장됩니다. 앱 재시작 또는 세션 종료 후 유지되지 않을 수 있으니 CSV로 내려받아 보관하세요.")
