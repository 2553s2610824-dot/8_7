import re
from datetime import datetime

import streamlit as st
import pandas as pd


# =========================
# 페이지 설정
# =========================
st.set_page_config(
    page_title="문자 예약 정리",
    page_icon="🍽️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #f7f8fc;
}
.main-title {
    font-size: 32px;
    font-weight: 800;
    color: #24324a;
}
.sub-title {
    color: #697386;
    font-size: 15px;
}
.reservation-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e7eaf0;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# 예약 데이터 초기화
# =========================
if "reservations" not in st.session_state:
    st.session_state.reservations = []


# =========================
# 예약 메시지 분석 함수
# =========================
def parse_reservation(text, source):
    result = {
        "time": "시간 미확인",
        "sort_time": "99:99",
        "people": "인원 미확인",
        "menu": [],
        "source": source,
        "message": text,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 예약 시간 분석
    time_match = re.search(
        r"(오전|오후)?\s*"
        r"([01]?\d|2[0-3])\s*시"
        r"(?:\s*([0-5]?\d)\s*분?)?",
        text
    )

    if time_match:
        period = time_match.group(1)
        hour = int(time_match.group(2))
        minute = int(time_match.group(3) or 0)

        if period == "오후" and hour < 12:
            hour += 12
        elif period == "오전" and hour == 12:
            hour = 0

        result["time"] = f"{hour:02d}:{minute:02d}"
        result["sort_time"] = f"{hour:02d}:{minute:02d}"

    else:
        # 14:30 또는 14시 30분과 같은 시간 형식
        time_match = re.search(
            r"(?<!\d)([01]?\d|2[0-3]):([0-5]\d)(?!\d)",
            text
        )

        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))

            result["time"] = f"{hour:02d}:{minute:02d}"
            result["sort_time"] = f"{hour:02d}:{minute:02d}"

    # 예약 인원 분석
    people_match = re.search(
        r"(\d+)\s*명",
        text
    )

    if people_match:
        result["people"] = f"{people_match.group(1)}명"

    # 메뉴와 수량 분석
    menu_keywords = [
        "아메리카노", "카페라떼", "라떼", "바닐라라떼",
        "아이스티", "에이드", "주스", "콜라", "사이다",
        "떡볶이", "김밥", "라면", "볶음밥", "돈까스",
        "파스타", "피자", "치킨", "샌드위치",
        "케이크", "빵", "쿠키", "샐러드", "빙수"
    ]

    for food in menu_keywords:
        if food not in text:
            continue

        # 메뉴 이름 뒤에 수량이 있는 경우
        pattern = (
            re.escape(food)
            + r"\s*(\d+)\s*(개|잔|그릇|인분|명)?"
        )
        quantity_match = re.search(pattern, text)

        if quantity_match:
            quantity = quantity_match.group(1)
            unit = quantity_match.group(2) or "개"
            result["menu"].append(
                f"{food} {quantity}{unit}"
            )
        else:
            result["menu"].append(food)

    # 중복 메뉴 제거
    result["menu"] = list(dict.fromkeys(result["menu"]))

    return result


# =========================
# 화면 제목
# =========================
st.markdown(
    '<div class="main-title">🍽️ 문자 예약 정리 사이트</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">'
    '문자와 메신저로 받은 예약을 한곳에서 정리하세요.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================
# 예약 현황
# =========================
reservations = st.session_state.reservations

total_count = len(reservations)
known_time_count = sum(
    1 for r in reservations
    if r["time"] != "시간 미확인"
)
known_people_count = sum(
    1 for r in reservations
    if r["people"] != "인원 미확인"
)

col1, col2, col3 = st.columns(3)

col1.metric("전체 예약", f"{total_count}건")
col2.metric("시간 확인", f"{known_time_count}건")
col3.metric("인원 확인", f"{known_people_count}건")

st.divider()


# =========================
# 예약 추가
# =========================
st.subheader("📝 새 예약 등록")

with st.form("reservation_form", clear_on_submit=True):
    source = st.selectbox(
        "예약을 받은 경로",
        ["문자(SMS)", "카카오톡", "인스타그램", "전화", "기타"]
    )

    message = st.text_area(
        "예약 메시지",
        placeholder=(
            "예시: 내일 오후 3시 30분에 4명 예약합니다. "
            "아메리카노 2잔, 떡볶이 1개"
        ),
        height=130
    )

    submitted = st.form_submit_button(
        "예약 분석 및 등록",
        use_container_width=True
    )

    if submitted:
        if not message.strip():
            st.warning("예약 메시지를 입력해 주세요.")
        else:
            reservation = parse_reservation(
                message.strip(),
                source
            )

            reservation["id"] = (
                datetime.now().strftime("%Y%m%d%H%M%S%f")
            )

            st.session_state.reservations.append(reservation)
            st.success("예약이 등록되었습니다.")
            st.rerun()


# =========================
# 예약 목록
# =========================
st.divider()
st.subheader("📋 예약 목록")

reservations = sorted(
    st.session_state.reservations,
    key=lambda r: (r["sort_time"], r["created"])
)

if not reservations:
    st.info("아직 등록된 예약이 없습니다.")

else:
    filter_source = st.selectbox(
        "예약 경로 필터",
        ["전체"] + list(dict.fromkeys(
            r["source"] for r in reservations
        ))
    )

    filtered = [
        r for r in reservations
        if filter_source == "전체"
        or r["source"] == filter_source
    ]

    st.caption(f"표시 중인 예약: {len(filtered)}건")

    for reservation in filtered:
        with st.container(border=True):
            left, right = st.columns([5, 1])

            with left:
                st.markdown(
                    f"### 🕒 {reservation['time']}"
                )
                st.write(
                    f"**인원:** {reservation['people']}"
                )
                st.write(
                    f"**접수 경로:** {reservation['source']}"
                )

                if reservation["menu"]:
                    st.write(
                        "**메뉴:** " + ", ".join(
                            reservation["menu"]
                        )
                    )
                else:
                    st.write("**메뉴:** 확인 필요")

                with st.expander("원본 예약 메시지 보기"):
                    st.write(reservation["message"])
                    st.caption(
                        f"등록 시간: {reservation['created']}"
                    )

            with right:
                if st.button(
                    "삭제",
                    key=f"delete_{reservation['id']}"
                ):
                    st.session_state.reservations = [
                        r for r in st.session_state.reservations
                        if r["id"] != reservation["id"]
                    ]
                    st.rerun()


# =========================
# 전체 예약 삭제
# =========================
st.divider()

if st.session_state.reservations:
    with st.expander("⚠️ 예약 데이터 관리"):
        st.warning(
            "전체 삭제를 누르면 현재 세션의 예약 목록이 모두 삭제됩니다."
        )

        confirm_delete = st.checkbox(
            "전체 예약을 삭제하겠습니다.",
            key="confirm_delete_all"
        )

        if st.button(
            "전체 예약 삭제",
            type="secondary",
            use_container_width=True
        ):
            if confirm_delete:
                st.session_state.reservations = []
                st.success("전체 예약이 삭제되었습니다.")
                st.rerun()
            else:
                st.error("먼저 확인 체크박스를 선택해 주세요.")
