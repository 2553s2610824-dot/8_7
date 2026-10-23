import streamlit as st
import pandas as pd
import datetime
import time

# ---페이지 기본 설정 ---
st.set_page_config(
    page_title="주문 폭주 자동 관리 시스템",
    page_icon="🍔",
    layout="wide"
)

# --- 세션 상태(Session State) 초기화 ---
if "pending_orders" not in st.get_state_keys():
    st.session_state.pending_orders = 8  # 초기 대기 주문 수
if "max_limit" not in st.get_state_keys():
    st.session_state.max_limit = 15     # 주문 제한 기준 (임계값)
if "time_per_order" not in st.get_state_keys():
    st.session_state.time_per_order = 3 # 주문 1건당 평균 소요 시간(분)
if "order_history" not in st.get_state_keys():
    st.session_state.order_history = []  # 주문 이력 저장

# --- 헤더 섹션 ---
st.title("🍔 스마트 주문 및 대기 관리 시스템")
st.markdown("현재 실시간 주문 상태를 자동으로 감지하여 최적의 대기 시간을 안내합니다.")
st.divider()

# --- 사이드바: 관리자 제어 패널 ---
st.sidebar.header("⚙️ 관리자 제어 패널")
st.sidebar.subheader("1. 시스템 설정")

st.session_state.max_limit = st.sidebar.number_input(
    "주문 제한 임계값 (최대 대기 수)",
    min_value=1,
    max_value=100,
    value=st.session_state.max_limit,
    help="대기 건수가 이 값을 초과하면 신규 주문이 자동으로 차단됩니다."
)

st.session_state.time_per_order = st.sidebar.number_input(
    "주문 1건당 평균 처리 시간 (분)",
    min_value=1,
    max_value=30,
    value=st.session_state.time_per_order
)

st.sidebar.subheader("2. 실시간 주문 관리")
col_admin1, col_admin2 = st.sidebar.columns(2)

with col_admin1:
    if st.button("✅ 주문 1건 완료"):
        if st.session_state.pending_orders > 0:
            st.session_state.pending_orders -= 1
            st.toast("주문 1건이 완료 처리되었습니다.", icon="✨")

with col_admin2:
    if st.button("➕ 강제 주문 추가"):
        st.session_state.pending_orders += 1
        st.toast("대기 주문 1건이 추가되었습니다.", icon="📩")

if st.sidebar.button("🚨 주문 폭주 상황 연출 (+10건)"):
    st.session_state.pending_orders += 10
    st.toast("주문 폭주 상황이 연출되었습니다!", icon="🔥")

if st.sidebar.button("🔄 상태 초기화"):
    st.session_state.pending_orders = 0
    st.toast("대기 상태가 초기화되었습니다.", icon="🧹")


# --- 메인 계산 로직 ---
current_pending = st.session_state.pending_orders
estimated_wait_time = current_pending * st.session_state.time_per_order
is_order_blocked = current_pending >= st.session_state.max_limit


# --- 상태 표시 섹션 (사용자 요청 핵심 화면) ---
if is_order_blocked:
    st.error("🚨 **현재 주문량이 너무 많습니다.** (신규 주문 일시 중단)")
else:
    st.success("🟢 **현재 주문이 가능합니다.**")

# 핵심 메트릭 카드 표시
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📌 현재 대기수", 
        value=f"{current_pending} 건",
        delta=f"최대 {st.session_state.max_limit}건 허용",
        delta_color="inverse" if is_order_blocked else "normal"
    )

with col2:
    st.metric(
        label="⏱️ 예상 대기시간", 
        value=f"약 {estimated_wait_time} 분",
        delta=f"건당 {st.session_state.time_per_order}분 소요"
    )

with col3:
    status_label = "주문 차단됨" if is_order_blocked else "주문 접수중"
    st.metric(
        label="📊 시스템 상태", 
        value=status_label
    )

st.divider()

# --- 고객 주문 접수 섹션 ---
st.subheader("📝 주문하기")

if is_order_blocked:
    st.warning("⚠️ 주문 폭주로 인해 잠시 후 다시 시도해 주세요. 기존 대기 주문이 처리되는 대로 즉시 재개됩니다.")
    
    # 비활성화된 폼 연출
    with st.expander("주문 입력폼 (현재 접수 중단)", expanded=False):
        st.text_input("고객명", disabled=True)
        st.multiselect("메뉴 선택", ["클래식 버거", "치즈 버거", "감자튀김", "콜라"], disabled=True)
        st.button("주문 접수 불가", disabled=True)
else:
    with st.form(key="order_form", clear_on_submit=True):
        customer_name = st.text_input("고객명 / 닉네임", placeholder="홍길동")
        selected_items = st.multiselect(
            "주문할 메뉴를 선택하세요",
            ["클래식 버거 세트", "치크 치즈버거", "크리스피 치킨버거", "양념 감자튀김", "제로 콜라"],
            default=["클래식 버거 세트"]
        )
        notes = st.text_input("요청사항", placeholder="예: 피클 빼주세요")
        
        submit_button = st.form_submit_button("🚀 주문 제출하기")

        if submit_button:
            if not customer_name.strip():
                st.error("고객명을 입력해 주세요.")
            elif not selected_items:
                st.error("최소 하나 이상의 메뉴를 선택해 주세요.")
            else:
                # 주문 성공 처리
                st.session_state.pending_orders += 1
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                st.session_state.order_history.append({
                    "시각": now_str,
                    "고객명": customer_name,
                    "메뉴": ", ".join(selected_items),
                    "요청사항": notes
                })
                st.balloons()
                st.success(f"🎉 {customer_name}님, 주문이 완료되었습니다! (예상 대기시간: 약 {st.session_state.pending_orders * st.session_state.time_per_order}분)")
                time.sleep(1)
                st.rerun()

st.divider()

# --- 실시간 주문 내역 모니터링 ---
st.subheader("📋 최근 주문 데이터 (실시간)")
if st.session_state.order_history:
    df = pd.DataFrame(st.session_state.order_history)
    st.dataframe(df.iloc[::-1], use_container_width=True) # 최신순 정렬
else:
    st.info("아직 접수된 주문 이력이 없습니다.")
