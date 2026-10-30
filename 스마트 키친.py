
import streamlit as st
import calendar
from datetime import date

# =====================================
# 기본 설정
# =====================================
st.set_page_config(
    page_title="Smart Kitchen",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

today = date.today()

# =====================================
# 디자인 CSS
# =====================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(circle at 10% 10%, #dce7fa, transparent 35%),
        radial-gradient(circle at 90% 90%, #d9eee7, transparent 35%),
        linear-gradient(135deg, #aebfdf, #d4e0ef, #c6d8d8);
    font-family: 'Noto Sans KR', sans-serif;
    color: #34485f;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.top-header {
    background: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.4);
    border-radius: 28px;
    padding: 25px 30px;
    margin-bottom: 25px;
}

.logo {
    font-size: 35px;
    font-weight: 800;
    color: white;
}

.subtitle {
    color: white;
    font-size: 14px;
    margin-top: 5px;
}

.date-text {
    color: white;
    font-size: 14px;
    text-align: right;
}

.section-title {
    color: white;
    font-size: 21px;
    font-weight: 800;
    margin: 22px 0 15px;
}

.dashboard-card {
    border-radius: 27px;
    padding: 23px;
    min-height: 205px;
    margin-bottom: 12px;
    box-shadow: 0 8px 22px rgba(55,75,100,0.10);
    color: #34485f;
}

.pink {
    background: #f3d0d1;
}

.orange {
    background: #f9e5d1;
}

.blue {
    background: #d0def5;
}

.green {
    background: #dcebd7;
}

.white {
    background: rgba(255,255,255,0.94);
}

.teal {
    background: #83b6bf;
    color: white;
}

.navy {
    background: #455c79;
    color: white;
}

.card-icon {
    font-size: 32px;
    margin-bottom: 12px;
}

.card-title {
    font-size: 19px;
    font-weight: 800;
    margin-bottom: 10px;
}

.card-description {
    font-size: 13px;
    line-height: 1.8;
    opacity: 0.85;
}

.calendar-table {
    width: 100%;
    text-align: center;
    border-collapse: collapse;
    font-size: 13px;
    color: #61768e;
}

.calendar-table th {
    padding: 9px 0;
    color: #8b9db1;
}

.calendar-table td {
    padding: 9px 0;
}

.today {
    background: #789bc7;
    color: white;
    border-radius: 50%;
    font-weight: bold;
}

.metric-number {
    font-size: 29px;
    font-weight: 800;
    color: #56799f;
}

.metric-label {
    color: #8294a9;
    font-size: 13px;
}

.info-box {
    background: rgba(255,255,255,0.88);
    border-radius: 22px;
    padding: 20px;
    min-height: 155px;
    color: #526b85;
    line-height: 1.9;
    font-size: 13px;
}

div.stButton > button {
    width: 100%;
    border-radius: 14px;
    min-height: 42px;
    background: rgba(255,255,255,0.85);
    color: #405a76;
    border: 1px solid rgba(255,255,255,0.8);
    font-weight: 700;
}

div.stButton > button:hover {
    background: #dceafa;
    color: #294d70;
    border-color: #8baed4;
}

@media(max-width: 700px) {
    .logo {
        font-size: 26px;
    }
    .dashboard-card {
        min-height: 170px;
    }
}
</style>
""", unsafe_allow_html=True)


# =====================================
# 상단 헤더
# =====================================
st.markdown(f"""
<div class="top-header">
    <div class="logo">🍳 SMART KITCHEN</div>
    <div class="subtitle">
        SMART MANAGEMENT SYSTEM
    </div>
    <div class="date-text">
        {today.strftime('%Y년 %m월 %d일')}
    </div>
</div>
""", unsafe_allow_html=True)


# =====================================
# 달력 생성
# =====================================
st.markdown(
    '<div class="section-title">오늘의 스마트 키친</div>',
    unsafe_allow_html=True
)

month_calendar = calendar.Calendar(
    firstweekday=6
).monthdayscalendar(today.year, today.month)

with st.container():
    st.markdown("""
    <div class="dashboard-card white"
         style="min-height:130px;">
        <div class="card-title">📅 TODAY</div>
        <div class="metric-number">
    """ + today.strftime("%Y.%m.%d") + """
        </div>
        <div class="metric-label">
            오늘의 주방 운영 일정을 확인하세요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="dashboard-card white"
         style="min-height:190px;">
        <div class="card-title">🗓️ 월간 달력</div>
    """, unsafe_allow_html=True)

    weekdays = ["일", "월", "화", "수", "목", "금", "토"]

    html = '<table class="calendar-table"><tr>'

    for day in weekdays:
        html += f"<th>{day}</th>"

    html += "</tr>"

    for week in month_calendar:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td></td>"
            elif day == today.day:
                html += f'<td><span class="today">{day}</span></td>'
            else:
                html += f"<td>{day}</td>"
        html += "</tr>"

    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# =====================================
# 주요 서비스 메뉴
# =====================================
st.markdown(
    '<div class="section-title">OUR SERVICES</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    st.markdown("""
    <div class="dashboard-card pink">
        <div class="card-icon">🤖</div>
        <div class="card-title">AI 주방 매니저</div>
        <div class="card-description">
            AI를 활용하여 주방 운영과
            식재료 관리를 효율적으로 도와주는 서비스
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="dashboard-card orange">
        <div class="card-icon">📞</div>
        <div class="card-title">전화 실시간 정리표</div>
        <div class="card-description">
            전화로 전달받은 주문 및
            문의 내용을 정리하는 서비스
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="dashboard-card blue">
        <div class="card-icon">📦</div>
        <div class="card-title">주문 폭주 자동 방어 시스템</div>
        <div class="card-description">
            주문이 한꺼번에 몰리는 상황에서
            주문 현황을 관리하는 서비스
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="dashboard-card green">
        <div class="card-icon">💬</div>
        <div class="card-title">문자 예약 정리 사이트</div>
        <div class="card-description">
            문자로 전달받은 예약 정보를
            편리하게 정리하는 서비스
        </div>
    </div>
    """, unsafe_allow_html=True)


# =====================================
# 하단 추가 구성
# =====================================
st.markdown(
    '<div class="section-title">SMART KITCHEN GUIDE</div>',
    unsafe_allow_html=True
)

left, middle, right = st.columns(3, gap="medium")

with left:
    st.markdown("""
    <div class="dashboard-card white">
        <div class="card-icon">✨</div>
        <div class="card-title">스마트한 주방 관리</div>
        <div class="card-description">
            여러 가지 주방 업무를 하나의 앱에서
            편리하게 확인하고 관리할 수 있습니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

with middle:
    st.markdown("""
    <div class="dashboard-card teal">
        <div class="card-icon">⏱️</div>
        <div class="card-title">시간 절약</div>
        <div class="card-description">
            반복되는 주방 업무를 효율적으로 정리하여
            불필요한 시간과 노력을 줄여줍니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="dashboard-card navy">
        <div class="card-icon">📱</div>
        <div class="card-title">간편한 통합 시스템</div>
        <div class="card-description">
            네 가지 주요 서비스를 한곳에 모아
            필요한 기능을 쉽게 찾아볼 수 있습니다.
        </div>
    </div>
    """, unsafe_allow_html=True)


# =====================================
# 하단 안내
# =====================================
st.markdown("""
<div style="
    text-align:center;
    color:white;
    padding:25px 0 5px;
    font-size:13px;
    line-height:2;">
    🍳 SMART KITCHEN<br>
    편리하고 효율적인 주방 관리의 시작
</div>
""", unsafe_allow_html=True)

