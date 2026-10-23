import os
from datetime import date, timedelta

import streamlit as st

# Gemini 라이브러리 오류가 발생해도 기본 앱은 실행
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


# =========================
# 1. 기본 설정
# =========================
st.set_page_config(
    page_title="AI 주방매니저",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.stApp {
    background-color: #f6f8f6;
}
[data-testid="stSidebar"] {
    background-color: #183b2d;
}
[data-testid="stSidebar"] * {
    color: #ffffff;
}
.hero {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(120deg, #183b2d, #43835b);
    color: white;
    margin-bottom: 20px;
}
.hero h1 {
    color: white;
    margin-bottom: 8px;
}
.hero p {
    color: #e7f4e9;
    margin-bottom: 0;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e4ebe5;
    padding: 15px;
    border-radius: 14px;
}
.stButton > button {
    border-radius: 9px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# =========================
# 2. 예시 데이터
# =========================
def make_inventory():
    today = date.today()
    return [
        {
            "id": 1, "name": "쌀", "category": "곡류",
            "qty": 12.0, "unit": "kg", "minimum": 5.0,
            "expiry": today + timedelta(days=90), "price": 3200.0
        },
        {
            "id": 2, "name": "돼지고기", "category": "육류",
            "qty": 3.2, "unit": "kg", "minimum": 4.0,
            "expiry": today + timedelta(days=2), "price": 12500.0
        },
        {
            "id": 3, "name": "양파", "category": "채소",
            "qty": 2.0, "unit": "kg", "minimum": 3.0,
            "expiry": today + timedelta(days=5), "price": 2800.0
        },
        {
            "id": 4, "name": "달걀", "category": "알류",
            "qty": 18.0, "unit": "개", "minimum": 10.0,
            "expiry": today + timedelta(days=12), "price": 300.0
        },
        {
            "id": 5, "name": "두부", "category": "가공식품",
            "qty": 6.0, "unit": "모", "minimum": 4.0,
            "expiry": today + timedelta(days=3), "price": 1800.0
        },
        {
            "id": 6, "name": "대파", "category": "채소",
            "qty": 0.5, "unit": "kg", "minimum": 1.0,
            "expiry": today + timedelta(days=4), "price": 4200.0
        },
    ]


def make_reservations():
    today = date.today()
    return [
        {
            "id": 1, "name": "김민지", "guests": 4,
            "day": today, "time": "18:00", "channel": "전화",
            "status": "예약 확정", "memo": "창가 자리 요청"
        },
        {
            "id": 2, "name": "박준호", "guests": 2,
            "day": today, "time": "19:00", "channel": "문자",
            "status": "예약 확정", "memo": ""
        },
        {
            "id": 3, "name": "이서연", "guests": 6,
            "day": today + timedelta(days=1), "time": "12:30",
            "channel": "메신저", "status": "확인 필요",
            "memo": "유아 의자 1개"
        },
    ]


if "inventory" not in st.session_state:
    st.session_state.inventory = make_inventory()

if "reservations" not in st.session_state:
    st.session_state.reservations = make_reservations()

if "next_item_id" not in st.session_state:
    st.session_state.next_item_id = 7

if "next_reservation_id" not in st.session_state:
    st.session_state.next_reservation_id = 4


# =========================
# 3. 공통 함수
# =========================
def won(value):
    return f"{value:,.0f}원"


def days_left(expiry):
    return (expiry - date.today()).days


def low_stock():
    return [
        item for item in st.session_state.inventory
        if item["qty"] < item["minimum"]
    ]


def expiring_soon():
    return [
        item for item in st.session_state.inventory
        if 0 <= days_left(item["expiry"]) <= 7
    ]


def inventory_value():
    return sum(
        item["qty"] * item["price"]
        for item in st.session_state.inventory
    )


def get_gemini_client():
    api_key = None

    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or genai is None:
        return None

    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


def create_ai_plan(budget, customers):
    items = st.session_state.inventory

    inventory_text = "\n".join([
        (
            f"{item['name']}: 현재 {item['qty']}{item['unit']}, "
            f"최소 재고 {item['minimum']}{item['unit']}, "
            f"유통기한 {item['expiry']}, "
            f"단가 {item['price']}원"
        )
        for item in items
    ])

    client = get_gemini_client()

    if client is None:
        return None, "API 키를 설정하지 않았거나 AI 라이브러리를 사용할 수 없습니다."

    prompt = f"""
당신은 소규모 식당의 주방 운영을 돕는 AI 매니저입니다.

현재 재고:
{inventory_text}

이번 장보기 예산: {budget:,}원
하루 예상 식사 인원: {customers}명

다음 형식으로 한국어 장보기 계획을 작성하세요.
1. 긴급 구매 품목
2. 추가 구매 권장 품목
3. 유통기한이 임박한 재료의 우선 활용 방법
4. 예산을 고려한 구매 순서
5. 장보기 체크리스트

재고 수량이 최소 기준보다 적은 재료를 우선 고려하세요.
입력되지 않은 판매량이나 가격은 사실처럼 단정하지 마세요.
가격은 입력된 단가를 바탕으로 한 추정임을 알려 주세요.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=900,
            ),
        )

        result = getattr(response, "text", None)

        if result and result.strip():
            return result.strip(), None

        return None, "AI 응답이 비어 있습니다. 잠시 후 다시 시도해 주세요."

    except Exception as exc:
        return None, (
            "AI 요청에 실패했습니다. API 키, 모델 사용 가능 여부, "
            f"사용량 한도를 확인해 주세요. 오류 유형: {type(exc).__name__}"
        )


# =========================
# 4. 사이드바 메뉴
# =========================
with st.sidebar:
    st.markdown("## 🍳 AI 주방매니저")
    st.caption("작은 식당을 위한 스마트 관리 도구")
    st.markdown("---")

    page = st.radio(
        "메뉴 선택",
        [
            "대시보드",
            "AI 재고 분석",
            "재고 관리",
            "유통기한 관리",
            "AI 장보기 추천",
            "예약 통합 관리",
        ],
    )

    st.markdown("---")
    st.markdown("### 오늘의 체크")
    st.write(f"🛒 재고 부족: {len(low_stock())}종")
    st.write(f"⏰ 7일 이내 기한 도래: {len(expiring_soon())}종")

    today_count = sum(
        1 for item in st.session_state.reservations
        if item["day"] == date.today()
        and item["status"] != "취소"
    )
    st.write(f"📞 오늘 예약: {today_count}건")

    st.caption(
        "예시 데이터로 시작합니다. "
        "현재 버전은 세션 기반으로 동작합니다."
    )


# =========================
# 5. 상단 제목
# =========================
st.markdown("""
<div class="hero">
    <h1>🍳 주방 운영, 한 화면에서 똑똑하게.</h1>
    <p>
        재고 분석부터 유통기한, 장보기, 예약까지
        한곳에서 관리하세요.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================
# 6. 대시보드
# =========================
if page == "대시보드":
    st.subheader("📊 오늘의 주방 현황")

    today = date.today()

    today_reservations = [
        item for item in st.session_state.reservations
        if item["day"] == today and item["status"] != "취소"
    ]

    urgent_expiry = [
        item for item in st.session_state.inventory
        if 0 <= days_left(item["expiry"]) <= 3
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "등록 재료",
        f"{len(st.session_state.inventory)}종"
    )
    col2.metric("재고 부족", f"{len(low_stock())}종")
    col3.metric("유통기한 임박", f"{len(urgent_expiry)}종")
    col4.metric("오늘 예약", f"{len(today_reservations)}건")

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.subheader("📦 확인이 필요한 재고")

        priority = sorted(
            st.session_state.inventory,
            key=lambda item: (
                item["qty"] >= item["minimum"],
                days_left(item["expiry"])
            )
        )

        if not priority:
            st.info("등록된 재료가 없습니다.")
        else:
            for item in priority[:6]:
                st.markdown(
                    f"**{item['name']}** — "
                    f"{item['qty']:g} {item['unit']}"
                )

                if item["qty"] < item["minimum"]:
                    st.warning("최소 재고 기준보다 부족합니다.")
                elif days_left(item["expiry"]) <= 3:
                    st.warning("유통기한이 임박했습니다.")
                else:
                    st.caption(
                        f"최소 기준 {item['minimum']:g} "
                        f"{item['unit']} · 유통기한 {item['expiry']}"
                    )

    with right:
        st.subheader("📅 오늘의 예약")

        if not today_reservations:
            st.info("오늘 예정된 예약이 없습니다.")

        for item in sorted(
            today_reservations,
            key=lambda value: value["time"]
        ):
            st.markdown(
                f"**{item['time']} · {item['name']}** "
                f"({item['guests']}명)"
            )
            st.caption(
                f"접수: {item['channel']} · 상태: {item['status']}"
            )

    st.markdown("---")
    st.subheader("💰 재고 현황")

    col1, col2 = st.columns(2)
    col1.metric("재고 추정 금액", won(inventory_value()))
    col2.metric("구매 확인 품목", f"{len(low_stock())}종")

    if st.session_state.inventory:
        st.caption("현재 수량과 최소 재고 기준의 비교")
        st.bar_chart({
            item["name"]: item["qty"] / max(item["minimum"], 1)
            for item in st.session_state.inventory
        })


# =========================
# 7. AI 재고 분석
# =========================
elif page == "AI 재고 분석":
    st.subheader("🧠 AI 재고 분석")
    st.write(
        "현재 수량과 최소 재고 기준을 비교해 "
        "부족한 재료와 우선 관리 품목을 확인합니다."
    )

    items = st.session_state.inventory

    if not items:
        st.info("재고 관리 메뉴에서 재료를 등록해 주세요.")
    else:
        low = low_stock()

        col1, col2 = st.columns(2)
        col1.metric("전체 재료", f"{len(items)}종")
        col2.metric("부족한 재료", f"{len(low)}종")

        if low:
            st.warning("구매를 검토해야 할 재료가 있습니다.")

            for item in low:
                missing = item["minimum"] - item["qty"]
                estimate = missing * item["price"]

                st.markdown(
                    f"- **{item['name']}**: "
                    f"{missing:g}{item['unit']} 부족, "
                    f"예상 보충 비용 {won(estimate)}"
                )
        else:
            st.success("모든 재료가 최소 재고 기준 이상입니다.")

        st.markdown("### 유통기한 확인")

        soon = expiring_soon()

        if soon:
            for item in sorted(soon, key=lambda x: x["expiry"]):
                st.write(
                    f"- {item['name']}: "
                    f"{days_left(item['expiry'])}일 남음"
                )
        else:
            st.success("7일 이내 유통기한이 도래하는 재료가 없습니다.")

        st.markdown("### 재고 분석 의견")

        if st.button("AI 분석 의견 생성", type="primary"):
            budget = 50000
            customers = 30

            with st.spinner("AI가 재고를 분석하고 있습니다..."):
                result, error = create_ai_plan(budget, customers)

            if result:
                st.markdown(result)
            else:
                st.warning(error)
                st.info(
                    "위의 재고 부족 목록과 유통기한 정보를 "
                    "기본 분석 결과로 활용할 수 있습니다."
                )


# =========================
# 8. 재고 관리
# =========================
elif page == "재고 관리":
    st.subheader("📦 재고 관리")
    st.caption("재료를 등록하고 수량, 단가, 유통기한을 관리하세요.")

    with st.expander("➕ 새 재료 등록", expanded=True):
        with st.form("add_inventory"):
            col1, col2, col3 = st.columns(3)

            name = col1.text_input("재료명")
            category = col2.selectbox(
                "분류",
                ["채소", "육류", "해산물", "곡류", "알류", "가공식품", "조미료", "기타"]
            )
            unit = col3.selectbox(
                "단위",
                ["kg", "g", "개", "모", "L", "병", "팩", "봉", "박스"]
            )

            col4, col5, col6 = st.columns(3)

            qty = col4.number_input(
                "현재 수량", min_value=0.0, value=1.0, step=0.5
            )
            minimum = col5.number_input(
                "최소 재고 기준", min_value=0.0, value=1.0, step=0.5
            )
            price = col6.number_input(
                "단가(원)", min_value=0.0, value=1000.0, step=100.0
            )

            expiry = st.date_input(
                "유통기한",
                value=date.today() + timedelta(days=7)
            )

            submitted = st.form_submit_button(
                "재료 등록",
                type="primary"
            )

            if submitted:
                if not name.strip():
                    st.error("재료명을 입력해 주세요.")
                else:
                    st.session_state.inventory.append({
                        "id": st.session_state.next_item_id,
                        "name": name.strip(),
                        "category": category,
                        "qty": float(qty),
                        "unit": unit,
                        "minimum": float(minimum),
                        "expiry": expiry,
                        "price": float(price),
                    })

                    st.session_state.next_item_id += 1
                    st.success("재료가 등록되었습니다.")
                    st.rerun()

    st.markdown("---")
    st.subheader("등록된 재료")

    search = st.text_input("재료 검색", placeholder="재료명 입력")

    filtered = [
        item for item in st.session_state.inventory
        if search.lower() in item["name"].lower()
    ]

    if not filtered:
        st.info("검색 결과가 없습니다.")
    else:
        for item in filtered:
            with st.container(border=True):
                col1, col2, col3 = st.columns([1.5, 1, 1])

                col1.markdown(f"### {item['name']}")
                col1.caption(item["category"])

                with col2:
                    st.write(
                        f"현재 수량: {item['qty']:g} {item['unit']}"
                    )
                    st.write(
                        f"최소 기준: {item['minimum']:g} {item['unit']}"
                    )

                with col3:
                    st.write(f"단가: {won(item['price'])}")
                    st.write(f"유통기한: {item['expiry']}")

                with st.expander("재고 수정 / 삭제"):
                    with st.form(f"edit_{item['id']}"):
                        new_qty = st.number_input(
                            "현재 수량",
                            min_value=0.0,
                            value=float(item["qty"]),
                            key=f"qty_{item['id']}"
                        )

                        new_minimum = st.number_input(
                            "최소 재고 기준",
                            min_value=0.0,
                            value=float(item["minimum"]),
                            key=f"minimum_{item['id']}"
                        )

                        new_price = st.number_input(
                            "단가(원)",
                            min_value=0.0,
                            value=float(item["price"]),
                            key=f"price_{item['id']}"
                        )

                        new_expiry = st.date_input(
                            "유통기한",
                            value=item["expiry"],
                            key=f"expiry_{item['id']}"
                        )

                        save = st.form_submit_button("변경사항 저장")

                        if save:
                            item["qty"] = float(new_qty)
                            item["minimum"] = float(new_minimum)
                            item["price"] = float(new_price)
                            item["expiry"] = new_expiry

                            st.success("수정했습니다.")
                            st.rerun()

                    if st.button(
                        "이 재료 삭제",
                        key=f"delete_{item['id']}"
                    ):
                        st.session_state.inventory = [
                            x for x in st.session_state.inventory
                            if x["id"] != item["id"]
                        ]
                        st.rerun()

    if st.session_state.inventory:
        csv_lines = [
            "재료명,분류,수량,단위,최소기준,유통기한,단가"
        ]

        for item in st.session_state.inventory:
            csv_lines.append(
                f"{item['name']},{item['category']},"
                f"{item['qty']},{item['unit']},"
                f"{item['minimum']},{item['expiry']},{item['price']}"
            )

        st.download_button(
            "재고 목록 CSV 다운로드",
            data="\ufeff" + "\n".join(csv_lines),
            file_name="inventory.csv",
            mime="text/csv"
        )


# =========================
# 9. 유통기한 관리
# =========================
elif page == "유통기한 관리":
    st.subheader("⏰ 유통기한 관리")
    st.write("유통기한이 가까운 재료를 우선 확인하세요.")

    period = st.radio(
        "조회 범위",
        ["전체", "3일 이내", "7일 이내", "기한 지남"],
        horizontal=True
    )

    items = sorted(
        st.session_state.inventory,
        key=lambda item: item["expiry"]
    )

    if period == "3일 이내":
        items = [
            item for item in items
            if 0 <= days_left(item["expiry"]) <= 3
        ]
    elif period == "7일 이내":
        items = [
            item for item in items
            if 0 <= days_left(item["expiry"]) <= 7
        ]
    elif period == "기한 지남":
        items = [
            item for item in items
            if days_left(item["expiry"]) < 0
        ]

    if not items:
        st.success("해당하는 재료가 없습니다.")
    else:
        for item in items:
            left_days = days_left(item["expiry"])

            with st.container(border=True):
                st.markdown(f"### {item['name']}")
                st.write(
                    f"수량: {item['qty']:g} {item['unit']} · "
                    f"유통기한: {item['expiry']}"
                )

                if left_days < 0:
                    st.error(
                        "기한이 지났습니다. 식품 안전 기준에 따라 "
                        "사용 가능 여부를 확인하세요."
                    )
                elif left_days <= 3:
                    st.warning(f"유통기한까지 {left_days}일 남았습니다.")
                elif left_days <= 7:
                    st.info(f"유통기한까지 {left_days}일 남았습니다.")
                else:
                    st.success(f"유통기한까지 {left_days}일 남았습니다.")

    st.caption(
        "알림은 입력한 날짜를 기준으로 계산합니다. "
        "실제 식품 안전 판단을 대신하지 않습니다."
    )


# =========================
# 10. AI 장보기 추천
# =========================
elif page == "AI 장보기 추천":
    st.subheader("🛒 AI 장보기 추천")
    st.write(
        "부족한 재고와 유통기한을 바탕으로 "
        "장보기 우선순위를 추천합니다."
    )

    col1, col2 = st.columns(2)

    with col1:
        budget = st.number_input(
            "장보기 예산(원)",
            min_value=0,
            value=50000,
            step=5000
        )

    with col2:
        customers = st.number_input(
            "하루 예상 식사 인원",
            min_value=1,
            value=30,
            step=5
        )

    low = low_stock()
    soon = expiring_soon()

    st.markdown("### 자동 확인된 구매 후보")

    if low:
        for item in low:
            missing = item["minimum"] - item["qty"]
            cost = missing * item["price"]

            st.write(
                f"- **{item['name']}**: "
                f"{missing:g} {item['unit']} 부족 · "
                f"예상 비용 {won(cost)}"
            )
    else:
        st.success("최소 재고 기준보다 부족한 재료가 없습니다.")

    st.markdown("### 먼저 활용할 재료")

    if soon:
        for item in soon:
            st.write(
                f"- {item['name']}: "
                f"유통기한 {item['expiry']} "
                f"(D{days_left(item['expiry']):+d})"
            )
    else:
        st.write("7일 이내 유통기한이 도래하는 재료가 없습니다.")

    if st.button(
        "✨ AI 장보기 계획 만들기",
        type="primary",
        use_container_width=True
    ):
        with st.spinner("장보기 계획을 작성하고 있습니다..."):
            result, error = create_ai_plan(budget, customers)

        if result:
            st.session_state.shopping_plan = result
            st.session_state.shopping_error = None
        else:
            estimated = sum(
                (item["minimum"] - item["qty"]) * item["price"]
                for item in low
            )

            lines = ["### 기본 장보기 체크리스트"]

            for item in low:
                missing = item["minimum"] - item["qty"]
                lines.append(
                    f"- [ ] {item['name']} {missing:g}{item['unit']} 보충 "
                    f"(예상 {won(missing * item['price'])})"
                )

            if not low:
                lines.append(
                    "- [ ] 필수 재료는 최소 기준 이상입니다. "
                    "판매량을 확인한 뒤 필요한 재료만 구매하세요."
                )

            if soon:
                lines.append("\n### 먼저 활용할 재료")
                for item in soon:
                    lines.append(
                        f"- {item['name']}: "
                        f"{item['expiry']}까지 우선 활용 검토"
                    )

            lines.append(f"\n부족 재료 기준 예상 합계: {won(estimated)}")
            lines.append(
                "\n※ AI 연결 없이 재고 수량과 단가로 계산한 기본 목록입니다."
            )

            st.session_state.shopping_plan = "\n".join(lines)
            st.session_state.shopping_error = error

    if st.session_state.get("shopping_error"):
        st.warning(st.session_state.shopping_error)
        st.info("AI 대신 재고 기준으로 계산한 기본 목록을 표시합니다.")

    if st.session_state.get("shopping_plan"):
        st.markdown("---")
        st.markdown(st.session_state.shopping_plan)

        st.download_button(
            "장보기 계획 다운로드",
            data=st.session_state.shopping_plan,
            file_name="shopping_plan.txt",
            mime="text/plain"
        )


# =========================
# 11. 예약 통합 관리
# =========================
elif page == "예약 통합 관리":
    st.subheader("☎️ 예약 통합 관리")
    st.write(
        "전화, 문자, 메신저 예약을 한 화면에 기록해 "
        "예약 누락과 중복을 줄이세요."
    )

    with st.expander("➕ 새 예약 등록", expanded=True):
        with st.form("add_reservation"):
            col1, col2, col3 = st.columns(3)

            name = col1.text_input("예약자 이름")
            guests = col2.number_input(
                "예약 인원",
                min_value=1,
                max_value=100,
                value=2
            )
            channel = col3.selectbox(
                "접수 경로",
                ["전화", "문자", "메신저", "방문", "기타"]
            )

            col4, col5, col6 = st.columns(3)

            reservation_day = col4.date_input(
                "예약 날짜",
                value=date.today()
            )

            reservation_time = col5.selectbox(
                "예약 시간",
                [
                    f"{hour:02d}:{minute:02d}"
                    for hour in range(10, 23)
                    for minute in (0, 30)
                ]
            )

            status = col6.selectbox(
                "예약 상태",
                ["확인 필요", "예약 확정", "취소"]
            )

            memo = st.text_input("요청사항")

            submitted = st.form_submit_button(
                "예약 저장",
                type="primary"
            )

            if submitted:
                if not name.strip():
                    st.error("예약자 이름을 입력해 주세요.")
                else:
                    duplicate = any(
                        item["day"] == reservation_day
                        and item["time"] == reservation_time
                        and item["name"].strip().lower() == name.strip().lower()
                        and item["status"] != "취소"
                        for item in st.session_state.reservations
                    )

                    if duplicate:
                        st.warning(
                            "같은 날짜, 시간, 이름의 예약이 있습니다. "
                            "중복 여부를 확인해 주세요."
                        )
                    else:
                        st.session_state.reservations.append({
                            "id": st.session_state.next_reservation_id,
                            "name": name.strip(),
                            "guests": int(guests),
                            "day": reservation_day,
                            "time": reservation_time,
                            "channel": channel,
                            "status": status,
                            "memo": memo.strip(),
                        })

                        st.session_state.next_reservation_id += 1
                        st.success("예약을 저장했습니다.")
                        st.rerun()

    st.markdown("---")
    st.subheader("예약 목록")

    col1, col2 = st.columns(2)

    with col1:
        selected_day = st.date_input(
            "조회 날짜",
            value=date.today(),
            key="reservation_filter_day"
        )

    with col2:
        selected_status = st.selectbox(
            "상태 필터",
            ["전체", "확인 필요", "예약 확정", "취소"]
        )

    reservations = [
        item for item in st.session_state.reservations
        if item["day"] == selected_day
    ]

    if selected_status != "전체":
        reservations = [
            item for item in reservations
            if item["status"] == selected_status
        ]

    reservations.sort(key=lambda item: item["time"])

    st.write(f"조회 결과: {len(reservations)}건")

    if not reservations:
        st.info("해당 날짜의 예약이 없습니다.")

    for item in reservations:
        with st.container(border=True):
            col1, col2, col3 = st.columns([1.3, 1, 1])

            col1.markdown(
                f"### {item['time']} · {item['name']}"
            )
            col1.caption(f"인원: {item['guests']}명")

            col2.write(f"접수 경로: {item['channel']}")
            col2.write(f"상태: {item['status']}")

            if item["memo"]:
                col2.caption(f"요청사항: {item['memo']}")

            with col3:
                status_options = [
                    "확인 필요", "예약 확정", "취소"
                ]

                current_index = status_options.index(item["status"])

                new_status = st.selectbox(
                    "상태 변경",
                    status_options,
                    index=current_index,
                    key=f"status_{item['id']}"
                )

                if new_status != item["status"]:
                    item["status"] = new_status
                    st.rerun()

                if st.button(
                    "예약 삭제",
                    key=f"delete_reservation_{item['id']}"
                ):
                    st.session_state.reservations = [
                        reservation
                        for reservation in st.session_state.reservations
                        if reservation["id"] != item["id"]
                    ]
                    st.rerun()

    if st.session_state.reservations:
        csv_lines = [
            "날짜,시간,예약자,인원,접수경로,상태,요청사항"
        ]

        for item in sorted(
            st.session_state.reservations,
            key=lambda x: (x["day"], x["time"])
        ):
            safe_name = item["name"].replace(",", " ")
            safe_memo = item["memo"].replace(",", " ")

            csv_lines.append(
                f"{item['day']},{item['time']},{safe_name},"
                f"{item['guests']},{item['channel']},"
                f"{item['status']},{safe_memo}"
            )

        st.download_button(
            "전체 예약 CSV 다운로드",
            data="\ufeff" + "\n".join(csv_lines),
            file_name="reservations.csv",
            mime="text/csv"
        )

    st.info(
        "예약이 들어오면 즉시 기록하고, "
        "'확인 필요' 상태의 예약은 최종 확인 후 확정하세요."
    )


# =========================
# 12. 하단 안내
# =========================
st.markdown("---")
st.caption(
    "AI 주방매니저 | 재고 및 예약 관리용 프로토타입 | "
    "현재 데이터는 세션에 저장되며 영구 저장되지 않을 수 있습니다."
)
