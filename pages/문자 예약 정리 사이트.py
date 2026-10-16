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
