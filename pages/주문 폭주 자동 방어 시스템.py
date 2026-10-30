import streamlit as st
import datetime

# ---------------------------------------------------------
# 1. 페이지 설정 및 세션 상태 초기화
# ---------------------------------------------------------
st.set_page_config(
    page_title="주문 폭주 자동 방어 시스템",
    page_icon="🚨",
    layout="wide"
)

# 세션 데이터 초기화
if "waiting_count" not in st.session_state:
    st.session_state.waiting_count = 0  # 현재 대기수

if "max_capacity" not in st.session_state:
    st.session_state.max_capacity = 10  # 최대 수용 한도

if "avg_time_per_team" not in st.session_state:
    st.session_state.avg_time_per_team = 15  # 팀당 평균 소요시간 (분)

if "auto_guard_active" not in st.session_state:
    st.session_state.auto_guard_active = True  # 자동 방어 기능 활성화

if "order_history" not in st.session_state:
    st.session_state.order_history = []  # 최근 주문 접수 목록

# ---------------------------------------------------------
# 2. 사이드바 (운영 환경 설정)
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 매장 운영 설정")
    
    st.session_state.max_capacity = st.number_input(
        "최대 수용 가능 대기 팀 수",
        min_value=1,
        max_value=100,
        value=st.session_state.max_capacity,
        help="이 숫자에 도달하면 신규 주문이 자동으로 차단됩니다."
    )
    
    st.session_state.avg_time_per_team = st.number_input(
        "팀당 평균 대기/조리시간 (분)",
        min_value=1,
        max_value=60,
        value=st.session_state.avg_time_per_team,
        help="예상 대기시간 계산에 사용됩니다."
    )
    
    st.session_state.auto_guard_active = st.toggle(
        "주문 폭주 자동 방어 활성화",
        value=st.session_state.auto_guard_active
    )
    
    st.divider()
    if st.button("🔄 대기 수 초기화", type="secondary"):
        st.session_state.waiting_count = 0
        st.session_state.order_history = []
        st.rerun()

# ---------------------------------------------------------
# 3. 핵심 계산 및 상태 문구 판별
# ---------------------------------------------------------
current_waiting = st.session_state.waiting_count
estimated_wait_time = current_waiting * st.session_state.avg_time_per_team

is_limit_reached = current_waiting >= st.session_state.max_capacity
is_blocked = st.session_state.auto_guard_active and is_limit_reached

# ---------------------------------------------------------
# 4. 주문 차단 시 전체 배경 및 글자색 가독성 보완 CSS
# ---------------------------------------------------------
if is_blocked:
    st.markdown(
        """
        <style>
        /* 1. 메인 바탕만 경고 빨간색으로 변경 */
        .stApp {
            background-color: #990000 !important;
            transition: background-color 0.4s ease;
        }
        /* 2. 메인 타이틀만 선명한 흰색으로 표시 */
        .stApp > header, .stApp h1 {
            color: #ffffff !important;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        }
        /* 3. 흰색/회색 카드 박스 내부의 모든 라벨, 텍스트, 입력폼 라벨은 진한 검은색 유지 */
        div[data-testid="stForm"], div[data-testid="stVerticalBlock"] > div {
            color: #111111;
        }
        label, .stMarkdown, p, span {
            color: #111111 !important;
        }
        /* 상단 타이틀 예외 처리 (타이틀만 흰색 유지) */
        h1 span, h1 {
            color: #ffffff !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# 5. 실시간 상태 배너 & 지표 카드 UI
# ---------------------------------------------------------
st.title("🚨 주문 폭주 자동 방어 시스템")

# [1] 실시간 주문 상태 배너
if is_blocked:
    st.markdown(
        """
        <div style="
            background-color: #ff3333;
            border: 2px solid #ffffff;
            color: #ffffff !important;
            padding: 16px 20px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            text-align: center;
        ">
            ⛔ 현재 주문량이 너무 많습니다. <span style="font-size:16px; font-weight:normal; color:#ffffff !important;">(신규 주문 자동 차단 중)</span>
        </div>
        """,
        unsafe_allow_html=True
    )
elif is_limit_reached and not st.session_state.auto_guard_active:
    st.markdown(
        """
        <div style="
            background-color: #f5f5f5;
            border: 2px solid #8c8c8c;
            color: #262626 !important;
            padding: 16px 20px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
        ">
            ⚠️ 현재 주문량이 너무 많습니다. <span style="font-size:15px; font-weight:normal; color:#595959 !important;">(경고: 자동 방어가 꺼져 있습니다)</span>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div style="
            background-color: #434343;
            color: #ffffff !important;
            padding: 16px 20px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            🟢 현재 주문이 가능합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

# [2] 현재 대기수 & 예상 대기시간 카드
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div style="
            background-color: #ffffff;
            border: 2px solid #d9d9d9;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        ">
            <div style="color: #333333 !important; font-size: 16px; font-weight: bold; margin-bottom: 8px;">
                👥 현재 대기수:
            </div>
            <div style="color: #111111 !important; font-size: 38px; font-weight: 800; margin-bottom: 6px;">
                {current_waiting} 팀
            </div>
            <div style="color: #666666 !important; font-size: 13px;">
                (최대 {st.session_state.max_capacity}팀 수용 가능)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="
            background-color: #ffffff;
            border: 2px solid #d9d9d9;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        ">
            <div style="color: #333333 !important; font-size: 16px; font-weight: bold; margin-bottom: 8px;">
                ⏱️ 예상 대기시간:
            </div>
            <div style="color: #111111 !important; font-size: 38px; font-weight: 800; margin-bottom: 6px;">
                약 {estimated_wait_time} 분
            </div>
            <div style="color: #666666 !important; font-size: 13px;">
                (팀당 평균 {st.session_state.avg_time_per_team}분 기준)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("") # 간격 조정

# ---------------------------------------------------------
# 6. 회색 카드 테두리로 감싼 기능 영역 (입력칸 글자 가독성 보완)
# ---------------------------------------------------------
left_col, right_col = st.columns([1, 1])

# --- [좌측] 신규 주문 / 예약 접수 카드 ---
with left_col:
    with st.container(border=True):
        st.markdown(
            """
            <div style="
                background-color: #f0f0f0;
                border-left: 5px solid #595959;
                padding: 10px 14px;
                border-radius: 4px;
                margin-bottom: 15px;
            ">
                <h4 style="margin: 0; color: #111111 !important;">📥 신규 주문 / 예약 접수</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        with st.form("order_form", clear_on_submit=True):
            customer_info = st.text_input("고객명 / 연락처 뒷자리", placeholder="예: 홍길동 / 5678")
            channel = st.selectbox("접수 채널", ["전화", "문자/메신저", "현장 방문", "배달 앱"])
            memo = st.text_input("주문 내용 및 요청사항", placeholder="예: 메인 메뉴 2개, 3명 방문")
            
            submit = st.form_submit_button("주문 등록", use_container_width=True)
            
            if submit:
                if not customer_info.strip():
                    st.error("고객 정보를 입력해주세요.")
                elif is_blocked:
                    st.error("❌ 현재 주문량이 너무 많아 신규 주문을 등록할 수 없습니다.")
                else:
                    now_time = datetime.datetime.now().strftime("%H:%M:%S")
                    st.session_state.order_history.insert(0, {
                        "time": now_time,
                        "info": customer_info,
                        "channel": channel,
                        "memo": memo
                    })
                    st.session_state.waiting_count += 1
                    st.success(f"✅ 주문이 접수되었습니다. (현재 대기수: {st.session_state.waiting_count}팀)")
                    st.rerun()

# --- [우측] 대기 수 관리 & 최근 접수 내역 카드 ---
with right_col:
    # 1. 대기 수 관리 전체 카드
    with st.container(border=True):
        st.markdown(
            """
            <div style="
                background-color: #f0f0f0;
                border-left: 5px solid #595959;
                padding: 10px 14px;
                border-radius: 4px;
                margin-bottom: 15px;
            ">
                <h4 style="margin: 0; color: #111111 !important;">⚡ 대기 수 관리</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("➕ 수동 대기 1팀 추가", use_container_width=True):
                if is_blocked:
                    st.error("현재 주문량이 너무 많아 추가할 수 없습니다.")
                else:
                    st.session_state.waiting_count += 1
                    st.rerun()
                    
        with btn_col2:
            if st.button("➖ 손님 입장 / 조리 완료 (-1팀)", type="primary", use_container_width=True):
                if st.session_state.waiting_count > 0:
                    st.session_state.waiting_count -= 1
                    st.toast("대기 1팀이 처리되었습니다.")
                    st.rerun()
                else:
                    st.warning("현재 대기 중인 팀이 없습니다.")

    st.write("") # 간격

    # 2. 최근 접수 내역 전체 카드
    with st.container(border=True):
        st.markdown(
            """
            <div style="
                background-color: #f0f0f0;
                border-left: 5px solid #595959;
                padding: 10px 14px;
                border-radius: 4px;
                margin-bottom: 15px;
            ">
                <h4 style="margin: 0; color: #111111 !important;">📋 최근 접수 내역</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if not st.session_state.order_history:
            st.info("접수된 주문 내역이 없습니다.")
        else:
            for item in st.session_state.order_history[:5]:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #ffffff;
                        border: 1px solid #d9d9d9;
                        border-radius: 8px;
                        padding: 10px 14px;
                        margin-bottom: 8px;
                        font-size: 14px;
                    ">
                        <span style="color: #111111 !important;">⏱️ <b>[{item['time']}]</b> <b>{item['info']}</b> ({item['channel']})</span><br/>
                        <span style="color: #555555 !important;">📝 {item['memo'] if item['memo'] else '요청사항 없음'}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
