import re
from datetime import datetime, date, time
import streamlit as st

st.set_page_config(
    page_title="예약 보드",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 색상 설정 ────────────────────────────────────────────────────────────────
SOURCE_STYLES = {
    "카카오톡": {"bg": "#FFF2C7", "border": "#F2C14E", "text": "#614A00", "emoji": "💬"},
    "인스타그램": {"bg": "#F3E2F4", "border": "#B66BC4", "text": "#642C70", "emoji": "◎"},
    "문자": {"bg": "#DCECFB", "border": "#5C9BD5", "text": "#174B78", "emoji": "✉"},
}

# ── 디자인 ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .stApp { background: #F5F7FB; }
    .block-container { padding-top: 1.7rem; padding-bottom: 2rem; max-width: 1450px; }
    header[data-testid="stHeader"] { background: transparent; }
    .hero {
        background: linear-gradient(120deg, #18243B 0%, #263D61 100%);
        border-radius: 22px;
        padding: 25px 30px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 10px 28px rgba(25, 43, 72, .12);
    }
    .hero-title { font-size: 1.8rem; font-weight: 800; letter-spacing: -.5px; }
    .hero-sub { color: #D8E2F2; font-size: .95rem; margin-top: 5px; }
    .panel-heading { font-size: 1.12rem; font-weight: 800; color: #202B3D; margin-bottom: 3px; }
    .panel-sub { font-size: .84rem; color: #7A8495; margin-bottom: 15px; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border: 1px solid #E5EAF2;
        border-radius: 18px;
        box-shadow: 0 5px 20px rgba(25, 43, 72, .045);
    }
    div[data-testid="stTextArea"] textarea {
        border-radius: 12px;
        background: #FBFCFE;
        border-color: #DDE4EE;
        font-size: .95rem;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 10px;
        border-color: #DDE4EE;
    }
    div.stButton > button {
        border-radius: 11px;
        min-height: 2.8rem;
        font-weight: 700;
        border: 1px solid #D9E1EC;
    }
    div.stButton > button[kind="primary"] {
        background: #253B5D;
        border-color: #253B5D;
    }
    .reservation-card {
        padding: 15px 16px 14px 16px;
        border: 1px solid var(--card-border);
        border-left: 7px solid var(--card-border);
        border-radius: 14px;
        background: var(--card-bg);
        color: #263247;
        margin: 2px 2px 12px 2px;
        box-shadow: 0 3px 9px rgba(24, 36, 59, .035);
    }
    .reservation-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    .reservation-time { font-size: 1.28rem; font-weight: 800; letter-spacing: -.3px; }
    .reservation-people { font-size: .9rem; font-weight: 700; }
    .reservation-food { font-size: 1rem; font-weight: 600; margin-top: 8px; }
    .reservation-source { font-size: .78rem; margin-top: 9px; opacity: .8; }
    .empty-state {
        text-align: center;
        padding: 45px 18px;
        border: 1px dashed #CBD5E1;
        border-radius: 14px;
        color: #7A8495;
        background: #FAFBFD;
    }
    .empty-icon { font-size: 2rem; margin-bottom: 8px; }
    .small-note { font-size: .8rem; color: #7A8495; }
    div[data-testid="stMetric"] {
        background: #F7F9FC;
        border: 1px solid #E8EDF4;
        border-radius: 12px;
        padding: 10px 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="hero-title">📅 예약 보드</div>
      <div class="hero-sub">여러 채널로 들어오는 예약을 한눈에 · 가까운 예약부터 자동 정렬</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "reservations" not in st.session_state:
    st.session_state.reservations = []

def parse_reservation(raw_text: str):
    """예: 2명, 18:30, 파스타 / 인원: 2명, 시간: 18:30, 음식: 파스타"""
    text = raw_text.strip()
    if not text:
        return None, "예약 내용을 입력해 주세요."

    people_match = re.search(r"(\d+)\s*명", text)
    if not people_match:
        people_match = re.search(r"(?:인원|인원수)\s*[:：=]?\s*(\d+)", text)
    if not people_match:
        return None, "인원수를 찾지 못했어요. 예: 2명, 18:30, 파스타"
    people = int(people_match.group(1))

    time_match = re.search(r"(?<!\d)([01]?\d|2[0-3])\s*:\s*([0-5]\d)(?!\d)", text)
    if time_match:
        hour, minute = int(time_match.group(1)), int(time_match.group(2))
    else:
        time_match = re.search(r"(?<!\d)([01]?\d|2[0-3])\s*시(?:\s*([0-5]?\d)\s*분?)?", text)
        if not time_match:
            return None, "예약 시간을 찾지 못했어요. 예: 18:30 또는 18시 30분"
        hour, minute = int(time_match.group(1)), int(time_match.group(2) or 0)

    food_match = re.search(r"(?:음식|메뉴)\s*[:：=]\s*([^,\n/]+)", text)
    if food_match:
        food = food_match.group(1).strip()
    else:
        food_text = re.sub(r"(?:인원수?|음식|메뉴)\s*[:：=]?\s*", " ", text)
        food_text = re.sub(r"\d+\s*명", " ", food_text)
        food_text = re.sub(r"(?<!\d)([01]?\d|2[0-3])\s*:\s*[0-5]\d(?!\d)", " ", food_text)
        food_text = re.sub(r"(?<!\d)([01]?\d|2[0-3])\s*시(?:\s*[0-5]?\d\s*분?)?", " ", food_text)
        food_text = re.sub(r"[,，/|]+", " ", food_text)
        food = re.sub(r"\s+", " ", food_text).strip(" -·")
    if not food:
        return None, "음식 종류를 찾지 못했어요. 예: 2명, 18:30, 파스타"

    return {
        "people": people,
        "hour": hour,
        "minute": minute,
        "food": food,
        "datetime": datetime.combine(date.today(), time(hour, minute)),
        "raw": raw_text.strip(),
        "created": datetime.now().isoformat(timespec="seconds"),
    }, None

left, right = st.columns([0.92, 1.08], gap="large")

with left:
    with st.container(border=True):
        st.markdown('<div class="panel-heading">✍️ 예약 문자 입력</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">메시지를 복사해 붙여 넣고 채널을 선택하세요.</div>', unsafe_allow_html=True)

        source = st.selectbox("연락이 들어온 앱", list(SOURCE_STYLES.keys()))
        raw_text = st.text_area(
            "예약 내용",
            height=190,
            placeholder="예시: 2명, 18:30, 파스타\n\n또는\n인원: 2명 / 시간: 18:30 / 음식: 파스타",
            help="인원수, 예약 시간, 음식 종류가 포함된 문자를 붙여 넣어 주세요.",
            label_visibility="visible",
        )

        if st.button("＋  예약 추가", type="primary", use_container_width=True):
            reservation, error = parse_reservation(raw_text)
            if error:
                st.error(error)
            else:
                reservation["source"] = source
                reservation["id"] = reservation["created"]
                st.session_state.reservations.append(reservation)
                st.toast("예약을 추가했어요!", icon="✅")
                st.rerun()

        st.markdown("**입력 예시**")
        st.code("2명, 18:30, 파스타", language="text")
        st.code("인원: 4명 / 시간: 19:00 / 음식: 스테이크", language="text")
        st.markdown(
            '<div class="small-note">채널 색상은 카카오톡=노랑 · 인스타그램=보라 · 문자=파랑입니다.</div>',
            unsafe_allow_html=True,
        )

with right:
    with st.container(border=True):
        st.markdown('<div class="panel-heading">🗂️ 예약 정리표</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">이 영역 안에서 마우스 휠로 예약 목록만 스크롤할 수 있어요.</div>', unsafe_allow_html=True)

        reservations = st.session_state.reservations
        now = datetime.now()
        reservations = sorted(
            reservations,
            key=lambda item: (
                item["datetime"] < now,
                item["datetime"],
            ),
        )
        total_people = sum(item["people"] for item in reservations)
        m1, m2 = st.columns(2)
        m1.metric("등록된 예약", f"{len(reservations)}건")
        m2.metric("총 예약 인원", f"{total_people}명")

        # Streamlit의 고정 높이 컨테이너는 내부에 자체 스크롤바를 만듭니다.
        # 따라서 예약이 많아져도 오른쪽 목록 영역만 휠로 스크롤됩니다.
        with st.container(height=570, border=False):
            if reservations:
                for item in reservations:
                    style = SOURCE_STYLES[item["source"]]
                    time_label = f'{item["hour"]:02d}:{item["minute"]:02d}'
                    past = item["datetime"] < now
                    status = "지난 시간" if past else "예정"
                    st.markdown(
                        f"""
                        <div class="reservation-card"
                             style="--card-bg:{style['bg']}; --card-border:{style['border']};">
                          <div class="reservation-top">
                            <div class="reservation-time">{time_label}</div>
                            <div class="reservation-people">{item['people']}명 · {status}</div>
                          </div>
                          <div class="reservation-food">🍽️ {item['food']}</div>
                          <div class="reservation-source">{style['emoji']} {item['source']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    """
                    <div class="empty-state">
                      <div class="empty-icon">🗓️</div>
                      <b>아직 등록된 예약이 없어요.</b><br>
                      왼쪽에서 예약 문자를 입력해 추가해 주세요.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if reservations:
            if st.button("🗑️ 전체 예약 삭제", use_container_width=True):
                st.session_state.reservations = []
                st.rerun()

st.divider()
st.markdown(
    '<div class="small-note">현재 버전은 앱 실행 중에만 예약을 보관합니다. 앱을 다시 시작하면 예약이 사라질 수 있습니다. 날짜 선택·개별 수정/삭제·영구 저장은 다음 단계에서 추가할 수 있어요.</div>',
    unsafe_allow_html=True,
)
