import re
import json
import os
from datetime import datetime, date, time
import streamlit as st

st.set_page_config(
    page_title="예약 보드",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 예약 저장 파일
SAVE_FILE = "reservations.json"

SOURCE_STYLES = {
    "카카오톡": {"bg": "#FFF2C7", "border": "#F2C14E", "text": "#614A00", "emoji": "💬"},
    "인스타그램": {"bg": "#F3E2F4", "border": "#B66BC4", "text": "#642C70", "emoji": "◎"},
    "문자": {"bg": "#DCECFB", "border": "#5C9BD5", "text": "#174B78", "emoji": "✉"},
}

FOOD_EMOJI_RULES = [
    (("삼겹", "갈비", "스테이크", "불고기", "고기", "족발", "보쌈", "제육", "돈까스", "돈가스", "치킨", "닭", "오리", "돼지", "소고기", "양고기"), "🍖"),
    (("찌개", "국밥", "탕", "전골", "국", "수프", "스프"), "🍲"),
    (("밥", "볶음밥", "덮밥", "비빔밥", "공깃밥", "주먹밥", "김밥"), "🍚"),
    (("라면", "우동", "파스타", "국수", "냉면", "쫄면", "짬뽕", "짜장면", "면", "칼국수", "마라탕"), "🍜"),
    (("샐러드", "야채", "채소", "쌈", "나물"), "🥗"),
    (("회", "초밥", "생선", "새우", "조개", "해물", "오징어", "문어", "연어", "참치", "해산물"), "🐟"),
    (("만두", "전", "튀김", "감자", "고로케"), "🥟"),
    (("피자",), "🍕"),
    (("햄버거", "버거", "샌드위치"), "🍔"),
    (("빵", "베이글", "토스트", "크루아상"), "🥐"),
    (("떡볶이", "떡", "순대", "어묵", "김치"), "🍢"),
    (("커피", "라떼", "아메리카노", "주스", "쥬스", "콜라", "음료", "에이드", "차", "맥주", "소주", "물"), "🥤"),
    (("케이크", "디저트", "아이스크림", "빙수", "쿠키", "초콜릿", "푸딩"), "🍰"),
    (("계란", "달걀", "오믈렛", "계란찜"), "🍳"),
]


# 예약 파일에 저장
def save_reservations():
    try:
        saved_data = []

        for item in st.session_state.reservations:
            saved_item = item.copy()
            saved_item["datetime"] = item["datetime"].isoformat()
            saved_data.append(saved_item)

        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(saved_data, file, ensure_ascii=False, indent=4)

    except (OSError, TypeError, ValueError) as e:
        st.warning(f"예약 저장 중 문제가 발생했어요: {e}")


# 저장된 예약 불러오기
def load_reservations():
    if not os.path.exists(SAVE_FILE):
        return []

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            saved_data = json.load(file)

        for item in saved_data:
            item["datetime"] = datetime.fromisoformat(item["datetime"])

        return saved_data

    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return []


# 처음 실행할 때 저장된 예약 불러오기
if "reservations" not in st.session_state:
    st.session_state.reservations = load_reservations()


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .stApp { background: #F5F7FB; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1450px; }
    header[data-testid="stHeader"] { background: transparent; }
    .hero { background: linear-gradient(120deg, #18243B 0%, #263D61 100%); border-radius: 22px; padding: 25px 30px; color: white; margin-bottom: 22px; box-shadow: 0 10px 28px rgba(25,43,72,.12); }
    .hero-title { font-size: 1.8rem; font-weight: 800; letter-spacing: -.5px; }
    .hero-sub { color: #D8E2F2; font-size: .95rem; margin-top: 5px; }
    .panel-heading { font-size: 1.12rem; font-weight: 800; color: #202B3D; margin-bottom: 3px; }
    .panel-sub { font-size: .84rem; color: #7A8495; margin-bottom: 15px; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background: white; border: 1px solid #E5EAF2; border-radius: 18px; box-shadow: 0 5px 20px rgba(25,43,72,.045); }
    div[data-testid="stTextArea"] textarea { border-radius: 12px; background: #FBFCFE; border-color: #DDE4EE; font-size: .95rem; }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div { border-radius: 10px; border-color: #DDE4EE; }
    div.stButton > button { border-radius: 11px; min-height: 2.8rem; font-weight: 700; border: 1px solid #D9E1EC; }
    div.stButton > button[kind="primary"] { background: #253B5D; border-color: #253B5D; }
    .reservation-card { padding: 15px 16px 14px; border: 1px solid var(--card-border); border-left: 7px solid var(--card-border); border-radius: 14px; background: var(--card-bg); color: #263247; margin: 2px 2px 12px; box-shadow: 0 3px 9px rgba(24,36,59,.035); }
    .reservation-top { display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; }
    .reservation-time { font-size: 1.28rem; font-weight: 800; letter-spacing: -.3px; }
    .reservation-people { font-size: .9rem; font-weight: 700; }
    .menu-count { display: inline-block; font-size: .75rem; font-weight: 700; padding: 4px 8px; margin-top: 9px; border-radius: 999px; background: rgba(255,255,255,.72); border: 1px solid rgba(70,80,100,.12); }
    .food-row { display: flex; align-items: center; gap: 10px; padding: 9px 10px; margin-top: 8px; background: rgba(255,255,255,.66); border-radius: 12px; }
    .food-icon { display: flex; align-items: center; justify-content: center; flex: 0 0 45px; width: 45px; height: 45px; border-radius: 12px; background: rgba(255,255,255,.9); font-size: 1.8rem; }
    .food-name { flex: 1; min-width: 0; font-weight: 700; overflow-wrap: anywhere; }
    .food-quantity { font-size: .88rem; font-weight: 800; white-space: nowrap; }
    .reservation-source { font-size: .78rem; margin-top: 10px; opacity: .8; }
    .empty-state { text-align: center; padding: 45px 18px; border: 1px dashed #CBD5E1; border-radius: 14px; color: #7A8495; background: #FAFBFD; }
    .empty-icon { font-size: 2rem; margin-bottom: 8px; }
    .small-note { font-size: .8rem; color: #7A8495; }
    div[data-testid="stMetric"] { background: #F7F9FC; border: 1px solid #E8EDF4; border-radius: 12px; padding: 10px 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><div class="hero-title">📅 예약 보드</div><div class="hero-sub">여러 채널의 예약을 한눈에 · 가까운 예약부터 자동 정렬</div></div>',
    unsafe_allow_html=True,
)


def food_emoji(food_name: str) -> str:
    name = food_name.replace(" ", "")
    for keywords, emoji in FOOD_EMOJI_RULES:
        if any(keyword in name for keyword in keywords):
            return emoji
    return "🍽️"


def parse_food_items(food_text: str):
    cleaned = re.sub(r"^(?:음식|메뉴)\s*[:：=]\s*", "", food_text.strip())
    parts = re.split(r"\s*(?:[,，/＋+]\s*|\s+및\s+|\s+그리고\s+|\n+)\s*", cleaned)
    items = []

    for part in parts:
        part = part.strip(" \t-·")
        if not part:
            continue

        quantity_match = re.search(
            r"(?:\s+|^)(\d+)\s*(인분|개|그릇|잔|접시|병|명|세트|판|마리|줄|인)\s*$",
            part,
        )

        if quantity_match:
            quantity = int(quantity_match.group(1))
            unit = quantity_match.group(2)
            name = part[:quantity_match.start()].strip()
            quantity_label = f"{quantity}{unit}"
        else:
            name = part
            quantity_label = ""

        if name:
            items.append({
                "name": name,
                "emoji": food_emoji(name),
                "quantity": quantity_label,
            })

    return items


def parse_reservation(raw_text: str):
    text = raw_text.strip()

    if not text:
        return None, "예약 내용을 입력해 주세요."

    people_match = re.search(r"(\d+)\s*명", text)

    if not people_match:
        people_match = re.search(r"(?:인원|인원수)\s*[:：=]?\s*(\d+)", text)

    if not people_match:
        return None, "인원수를 찾지 못했어요. 예: 2명, 18:30, 음식: 파스타"

    people = int(people_match.group(1))

    # 날짜: 10월 28일, 10/28, 10-28, 2026년 10월 28일
    date_match = re.search(
        r"(?:(20\d{2})\s*년\s*)?(\d{1,2})\s*(?:월|[./-])\s*(\d{1,2})\s*(?:일)?",
        text,
    )

    if date_match:
        year = int(date_match.group(1) or date.today().year)
        month = int(date_match.group(2))
        day = int(date_match.group(3))

        try:
            reservation_date = date(year, month, day)
        except ValueError:
            return None, "날짜가 올바르지 않아요. 예: 10월 28일 또는 10/28"
    else:
        reservation_date = date.today()

    time_match = re.search(
        r"(?<!\d)([01]?\d|2[0-3])\s*:\s*([0-5]\d)(?!\d)",
        text,
    )

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
    else:
        time_match = re.search(
            r"(?<!\d)([01]?\d|2[0-3])\s*시(?:\s*([0-5]?\d)\s*분?)?",
            text,
        )

        if not time_match:
            return None, "예약 시간을 찾지 못했어요. 예: 18:30 또는 18시 30분"

        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)

    food_match = re.search(r"(?:음식|메뉴)\s*[:：=]\s*([^\n]+)", text)

    if food_match:
        food_text = food_match.group(1).strip()
    else:
        food_text = re.sub(r"\d+\s*명", " ", text)

        food_text = re.sub(
            r"(?:(?:20\d{2})\s*년\s*)?\d{1,2}\s*(?:월|[./-])\s*\d{1,2}\s*(?:일)?",
            " ",
            food_text,
        )

        food_text = re.sub(
            r"(?<!\d)([01]?\d|2[0-3])\s*:\s*[0-5]\d(?!\d)",
            " ",
            food_text,
        )

        food_text = re.sub(
            r"(?<!\d)([01]?\d|2[0-3])\s*시(?:\s*[0-5]?\d\s*분?)?",
            " ",
            food_text,
        )

        food_text = re.sub(r"(?:인원수?|시간)\s*[:：=]?", " ", food_text)
        food_text = re.sub(r"^[,，/|\s]+|[,，/|\s]+$", "", food_text)
        food_text = re.sub(r"^\s*[,，/|]+\s*", "", food_text)
        food_text = re.sub(r"\s+", " ", food_text).strip(" -·")

    food_items = parse_food_items(food_text)

    if not food_items:
        return None, "음식 종류를 찾지 못했어요. 예: 음식: 삼겹살 2인분, 된장찌개 1개"

    return {
        "people": people,
        "hour": hour,
        "minute": minute,
        "food": food_text,
        "food_items": food_items,
        "datetime": datetime.combine(reservation_date, time(hour, minute)),
        "raw": raw_text.strip(),
        "created": datetime.now().isoformat(timespec="seconds"),
    }, None


left, right = st.columns([0.92, 1.08], gap="large")

with left:
    with st.container(border=True):
        st.markdown(
            '<div class="panel-heading">✍️ 예약 문자 입력</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="panel-sub">메시지를 복사해 붙여 넣고 채널을 선택하세요.</div>',
            unsafe_allow_html=True,
        )

        source = st.selectbox("연락이 들어온 앱", list(SOURCE_STYLES.keys()))

        # 예약자명 입력
        customer_name = st.text_input(
            "예약자명",
            placeholder="예: 홍길동",
            help="입력한 예약자명이 오른쪽 예약 카드에도 표시됩니다.",
        )

        raw_text = st.text_area(
            "예약 내용",
            height=190,
            placeholder=(
                "예시: 10월 28일, 4명, 18:30, 삼겹살 2인분, 된장찌개 1개\n\n"
                "또는\n"
                "날짜: 10/28 / 인원: 4명 / 시간: 18:30 / 음식: 파스타 2개"
            ),
            help="날짜, 인원수, 예약 시간, 음식 종류를 포함한 문자를 붙여 넣어 주세요.",
        )

        if st.button("＋  예약 추가", type="primary", width="stretch"):
            reservation, error = parse_reservation(raw_text)

            if error:
                st.error(error)
            else:
                reservation["customer_name"] = customer_name.strip() or "이름 미입력"
                reservation["source"] = source
                reservation["id"] = reservation["created"]
                st.session_state.reservations.append(reservation)

                # 예약 추가 즉시 저장
                save_reservations()

                st.toast("예약을 추가하고 저장했어요!", icon="✅")
                st.rerun()

        st.markdown("**입력 예시**")
        st.code("10월 28일, 4명, 18:30, 삼겹살 2인분, 된장찌개 1개")
        st.code("날짜: 10/28 / 인원: 2명 / 시간: 19:00 / 음식: 파스타 2개, 콜라 2잔")

        st.markdown(
            '<div class="small-note">카카오톡=노랑 · 인스타그램=보라 · 문자=파랑</div>',
            unsafe_allow_html=True,
        )


with right:
    with st.container(border=True):
        st.markdown(
            '<div class="panel-heading">🗂️ 예약 정리표</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="panel-sub">예약 목록은 이 영역 안에서 스크롤할 수 있어요.</div>',
            unsafe_allow_html=True,
        )

        reservations = sorted(
            st.session_state.reservations,
            key=lambda item: (
                item.get("datetime", datetime.max) < datetime.now(),
                item.get("datetime", datetime.max),
            ),
        )

        total_people = sum(item["people"] for item in reservations)
        total_menu_kinds = sum(
            len(item.get("food_items", []))
            for item in reservations
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("등록된 예약", f"{len(reservations)}건")
        m2.metric("예약 인원", f"{total_people}명")
        m3.metric("메뉴 종류", f"{total_menu_kinds}종")

        with st.container(height=570, border=False):
            if reservations:
                for item in reservations:
                    style = SOURCE_STYLES[item["source"]]

                    time_label = f'{item["hour"]:02d}:{item["minute"]:02d}'
                    customer_name_label = item.get("customer_name", "이름 미입력")
                    date_label = item["datetime"].strftime("%m월 %d일")
                    weekday_label = [
                        "월", "화", "수", "목", "금", "토", "일"
                    ][item["datetime"].weekday()]

                    past = item["datetime"] < datetime.now()
                    status = "지난 시간" if past else "예정"

                    food_rows = "".join(
                        f'''<div class="food-row">
                            <div class="food-icon">{menu["emoji"]}</div>
                            <div class="food-name">{menu["name"]}</div>
                            <div class="food-quantity">{menu["quantity"]}</div>
                        </div>'''
                        for menu in item.get(
                            "food_items",
                            [{"name": item["food"], "emoji": "🍽️", "quantity": ""}],
                        )
                    )

                    menu_count = len(item.get("food_items", []))

                    st.markdown(
                        f'''<div class="reservation-card" style="--card-bg:{style["bg"]}; --card-border:{style["border"]};">
                            <div class="reservation-top">
                                <div>
                                    <div style="font-size:.95rem; font-weight:800; margin-bottom:4px;">
                                        👤 {customer_name_label}
                                    </div>
                                    <div class="reservation-time">{time_label}</div>
                                    <div style="font-size:.85rem; font-weight:700; margin-top:3px;">
                                        📅 {date_label} ({weekday_label})
                                    </div>
                                </div>
                                <div class="reservation-people">
                                    {item["people"]}명 · {status}
                                </div>
                            </div>
                            <div class="menu-count">🍽️ 메뉴 {menu_count}종</div>
                            {food_rows}
                            <div class="reservation-source">
                                {style["emoji"]} {item["source"]}
                            </div>
                        </div>''',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="empty-state"><div class="empty-icon">🗓️</div><b>아직 등록된 예약이 없어요.</b><br>왼쪽에서 예약 문자를 입력해 추가해 주세요.</div>',
                    unsafe_allow_html=True,
                )

        if reservations and st.button("🗑️ 전체 예약 삭제", width="stretch"):
            st.session_state.reservations = []

            # 삭제 내용도 저장 파일에 반영
            save_reservations()

            st.rerun()
