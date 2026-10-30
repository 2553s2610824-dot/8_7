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
# 현재 대기수 및 예상 대기시간 계산
current_waiting = st.session_state.waiting_count
estimated_wait_time = current_waiting * st.session_state.avg_time_per_team

# 수용 한도 초과 및 차단 여부
is_limit_reached = current_waiting >= st.session_state.max_capacity
is_blocked = st.session_state.auto_guard_active and is_limit_reached

# ---------------------------------------------------------
# 4. 실시간 상태 배너 & 영역별 커스텀 카드 UI
# ---------------------------------------------------------
st.title("🚨 주문 폭주 자동 방어 시스템")

# [1] 상태 안내 배너
if is_blocked:
    st.markdown(
        """
        <div style="
            background-color: #ffebe9;
            border: 2px solid #ff4d4f;
            color: #d90429;
            padding: 16px 20px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
        ">
            ⛔ 현재 주문량이 너무 많습니다. <span style="font-size:15px; font-weight:normal;">(신규 주문 자동 차단 중)</span>
        </div>
        """,
        unsafe_allow_html=True
    )
elif is_limit_reached and not st.session_state.auto_guard_active:
    st.markdown(
        """
        <div style="
            background-color: #fffbe6;
            border: 2px solid #ffe58f;
            color: #d48806;
            padding: 16px 20px;
            border-radius: 10px;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
        ">
            ⚠️ 현재 주문량이 너무 많습니다. <span style="font-size:15px; font-weight:normal;">(경고: 자동 방어가 꺼져 있습니다)</span>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <div style="
            background-color: #0b6623;
            color: #ffffff;
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

# [2] 현재 대기수 & 예상 대기시간 각각 카드형 테두리 적용
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div style="
            background-color: #f0f7ff;
            border: 2px solid #1890ff;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        ">
            <div style="color: #434343; font-size: 16px; font-weight: bold; margin-bottom: 8px;">
                👥 현재 대기수:
            </div>
            <div style="color: #0958d9; font-size: 38px; font-weight: 800; margin-bottom: 6px;">
                {current_waiting} 팀
            </div>
            <div style="color: #8c8c8c; font-size: 13px;">
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
            background-color: #fff7e6;
            border: 2px solid #ffa940;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        ">
            <div style="color: #434343; font-size: 16px; font-weight: bold; margin-bottom: 8px;">
                ⏱️ 예상 대기시간:
            </div>
            <div style="color: #d46b08; font-size: 38px; font-weight: 800; margin-bottom: 6px;">
                약 {estimated_wait_time} 분
            </div>
            <div style="color: #8c8c8c; font-size: 13px;">
                (팀당 평균 {st.session_state.avg_time_per_team}분 기준)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ---------------------------------------------------------
# 5. 주문 입력 및 대기 처리 기능
# ---------------------------------------------------------
left_col, right_col = st.columns([1, 1])

# --- [좌측] 신규 주문 접수폼 ---
with left_col:
    st.subheader("📥 신규 주문/예약 접수")
    
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

# --- [우측] 실시간 대기 차감/관리 ---
with right_col:
    st.subheader("⚡ 대기 수 관리")
    
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

    st.subheader("📋 최근 접수 내역")
    if not st.session_state.order_history:
        st.info("접수된 주문 내역이 없습니다.")
    else:
        for item in st.session_state.order_history[:5]:
            st.write(f"• [{item['time']}] **{item['info']}** ({item['channel']}) - {item['memo']}")
