import re
from datetime import datetime, date, time
import streamlit as st

st.set_page_config(
    page_title="예약 보드",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SOURCE_STYLES = {
    "카카오톡": {"bg": "#FFF2C7", "border": "#F2C14E", "text": "#614A00", "emoji": "💬"},
    "인스타그램": {"bg": "#F3E2F4", "border": "#B66BC4", "text": "#642C70", "emoji": "◎"},
    "문자": {"bg": "#DCECFB", "border": "#5C9BD5", "text": "#174B78", "emoji": "✉"},
}

# 음식 이름에 따라 카드에 붙일 그림 이모티콘을 고릅니다.
FOOD_EMOJI_RULES = [
    (("삼겹", "갈비", "스테이크", "불고기", "고기", "족발", "보쌈", "제육", "돈까스", "돈가스", "치킨", "닭", "오리", "돼지", "소고기", "양고기"), "🍖"),
    (("찌개", "국밥", "국수국물", "탕", "전골", "국", "수프", "스프"), "🍲"),
    (("밥", "볶음밥", "덮밥", "비빔밥", "공깃밥", "주먹밥", "초밥", "김밥"), "🍚"),
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

# 참고: 현재 버전은 브라우저 세션에만 저장합니다. 앱 재시작 후에도 보관되는 영구 저장 기능은 포함하지 않습니다.
if "reservations" not in st.session_state:
    st.session_state.reservations = []


def food_emoji(food_name: str) -> str:
    name = food_name.replace(" ", "")
    for keywords, emoji in FOOD_EMOJI_RULES:
        if any(keyword in name for keyword in keywords):
            return emoji
    return "🍽️"


def parse_food_items(food_text: str):
    """메뉴 문장을 메뉴별로 나누고, 적혀 있는 수량을 찾아냅니다."""
    cleaned = re.sub(r"^(?:음식|메뉴)\s*[:：=]\s*", "", food_text.strip())
    parts = re.split(r"\s*(?:[,，/＋+]\s*|\s+및\s+|\s+그리고\s+|\n+)\s*", cleaned)
    items = []
    for part in parts:
