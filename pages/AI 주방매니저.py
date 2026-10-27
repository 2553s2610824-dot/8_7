
import os
from datetime import date, datetime, time, timedelta

import streamlit as st
import pandas as pd

try:
    from google import genai
except ImportError:
    genai = None


# ==================================================
# 1. 기본 설정
# ==================================================
st.set_page_config(
    page_title="AI 주방매니저",
    page_icon="🍳",
    layout="wide",
)

st.title("🍳 AI 주방매니저")
st.caption("식재료 재고 · 유통기한 · 장보기 · 주문 · 예약을 한곳에서 관리하세요.")

TODAY = date.today()

# 음식 1개를 만들 때 사용하는 식재료 양
# 식재료 단위는 아래 기본 재고의 단위와 일치해야 합니다.
RECIPES = {
    "돼지고기 덮밥": {
        "돼지고기": 0.15,
        "쌀": 0.20,
        "양파": 0.05,
        "대파": 0.10,
    },
    "두부 덮밥": {
        "두부": 1,
        "쌀": 0.20,
        "양파": 0.05,
        "대파": 0.10,
    },
    "계란 덮밥": {
        "달걀": 1,
        "쌀": 0.20,
        "양파": 0.03,
        "대파": 0.10,
    },
}


# ==================================================
# 2. 초기 데이터
# ==================================================
def make_inventory():
    return [
        {
            "name": "쌀",
            "qty": 20.0,
            "unit": "kg",
            "minimum": 5.0,
            "price": 3000,
            "expiry": TODAY + timedelta(days=90),
        },
        {
            "name": "돼지고기",
            "qty": 5.0,
            "unit": "kg",
            "minimum": 2.0,
            "price": 12000,
            "expiry": TODAY + timedelta(days=3),
        },
        {
            "name": "양파",
            "qty": 8.0,
            "unit": "kg",
            "minimum": 2.0,
            "price": 2500,
            "expiry": TODAY + timedelta(days=10),
        },
        {
            "name": "달걀",
            "qty": 30.0,
            "unit": "개",
            "minimum": 10.0,
            "price": 300,
            "expiry": TODAY + timedelta(days=7),
        },
        {
            "name": "두부",
            "qty": 10.0,
            "unit": "모",
            "minimum": 3.0,
            "price": 1800,
            "expiry": TODAY + timedelta(days=2),
        },
        {
            "name": "대파",
            "qty": 8.0,
            "unit": "대",
            "minimum": 2.0,
            "price": 700,
            "expiry": TODAY + timedelta(days=5),
        },
    ]


def initialize_state():
    if "inventory" not in st.session_state:
        st.session_state.inventory = make_inventory()

    if "reservations" not in st.session_state:
        st.session_state.reservations = []

    if "orders" not in st.session_state:
        st.session_state.orders = []

    if "next_order_id" not in st.session_state:
        st.session_state.next_order_id = 1

    if "next_reservation_id" not in st.session_state:
        st.session_state.next_reservation_id = 1

    if "ai_stock_result" not in st.session_state:
        st.session_state.ai_stock_result = ""

    if "ai_shopping_result" not in st.session_state:
        st.session_state.ai_shopping_result = ""


initialize_state()


# ==================================================
# 3. 공통 함수
# ==================================================
def won(value):
    return f"{int(round(value)):,}원"


def get_item(name):
    for item in st.session_state.inventory:
        if item["name"] == name:
            return item
    return None


def low_stock():
    return [
        item
        for item in st.session_state.inventory
        if item["qty"] <= item["minimum"]
    ]


def expiring_soon(days=7):
    result = []

    for item in st.session_state.inventory:
        remaining_days = (item["expiry"] - TODAY).days

        if remaining_days <= days:
            result.append((item, remaining_days))

    return sorted(result, key=lambda x: x[1])


def inventory_value():
    return sum(
        item["qty"] * item["price"]
        for item in st.session_state.inventory
    )


def purchase_list():
    """최소 보유량을 기준으로 부족한 수량과 예상 구매비를 계산합니다."""
    result = []

    for item in low_stock():
        need = max(0, item["minimum"] - item["qty"])

        if need > 0:
            result.append({
                "식재료": item["name"],
                "현재 수량": item["qty"],
                "최소 보유량": item["minimum"],
                "구매 필요 수량": round(need, 2),
                "단위": item["unit"],
                "예상 비용": need * item["price"],
            })

    return result


def inventory_dataframe():
    rows = []

    for item in st.session_state.inventory:
        days = (item["expiry"] - TODAY).days

        if days < 0:
            expiry_status = "유통기한 지남"
        elif days <= 3:
            expiry_status = "긴급 확인"
        elif days <= 7:
            expiry_status = "임박"
        else:
            expiry_status = "정상"

        stock_status = (
            "재고 부족"
            if item["qty"] <= item["minimum"]
            else "정상"
        )

        rows.append({
            "식재료": item["name"],
            "현재 수량": item["qty"],
            "단위": item["unit"],
            "최소 보유량": item["minimum"],
            "단위 가격": won(item["price"]),
            "유통기한": item["expiry"].isoformat(),
            "남은 일수": days,
            "재고 상태": stock_status,
            "유통기한 상태": expiry_status,
        })

    return pd.DataFrame(rows)


def get_gemini_client():
    """Streamlit Secrets 또는 환경 변수에서 API 키를 가져옵니다."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY", "")

    if not api_key or genai is None:
        return None

    return genai.Client(api_key=api_key)


def ask_gemini(prompt):
    """Gemini에 요청하고 결과 문자열을 반환합니다."""
    client = get_gemini_client()

    if client is None:
        return (
            "AI 기능을 사용하려면 Streamlit Secrets에 "
            "GEMINI_API_KEY를 설정하고 google-genai 패키지를 설치해 주세요."
        )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
        )
        return response.text or "AI 응답이 비어 있습니다."
    except Exception as error:
        return (
            "AI 요청 중 오류가 발생했습니다. API 키, 모델 이름, "
            f"사용량 제한을 확인해 주세요.\n\n오류 내용: {error}"
        )


def format_inventory_for_ai():
    if not st.session_state.inventory:
        return "등록된 식재료가 없습니다."

    lines = []

    for item in st.session_state.inventory:
        days = (item["expiry"] - TODAY).days
        lines.append(
            f"- {item['name']}: {item['qty']} {item['unit']}, "
            f"최소 보유량 {item['minimum']} {item['unit']}, "
            f"유통기한 {item['expiry']} (남은 일수 {days}일), "
            f"단위 가격 {item['price']}원"
        )

    return "\n".join(lines)


# ==================================================
# 4. 사이드바 메뉴
# ==================================================
with st.sidebar:
    st.header("🍽️ 메뉴")

    page = st.radio(
        "관리할 기능을 선택하세요.",
        [
            "대시보드",
            "AI 재고 분석",
            "재고 관리",
            "유통기한 관리",
            "AI 장보기 추천",
            "주문 관리",
            "예약 통합 관리",
        ],
    )

    st.divider()
    st.caption("AI 주방매니저")
    st.caption("재고와 주문 데이터를 간편하게 관리하세요.")


# ==================================================
# 5. 대시보드
# ==================================================
if page == "대시보드":
    st.subheader("📊 오늘의 주방 현황")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "등록된 식재료",
        f"{len(st.session_state.inventory)}개",
    )
    col2.metric(
        "재고 부족 식재료",
        f"{len(low_stock())}개",
    )
    col3.metric(
        "유통기한 확인 필요",
        f"{len(expiring_soon())}개",
    )
    col4.metric(
        "재고 예상 가치",
        won(inventory_value()),
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("### ⚠️ 재고 부족")

        shortages = low_stock()

        if shortages:
            for item in shortages:
                st.warning(
                    f"**{item['name']}**: {item['qty']} {item['unit']} "
                    f"(최소 보유량 {item['minimum']} {item['unit']})"
                )
        else:
            st.success("현재 재고가 모두 최소 보유량을 넘습니다.")

    with right:
        st.markdown("### ⏰ 유통기한 확인")

        expiry_items = expiring_soon()

        if expiry_items:
            for item, days in expiry_items:
                if days < 0:
                    label = f"{abs(days)}일 지남"
                elif days == 0:
                    label = "오늘까지"
                else:
                    label = f"{days}일 남음"

                st.warning(
                    f"**{item['name']}**: {item['expiry']} ({label})"
                )
        else:
            st.success("앞으로 7일 이내에 확인할 식재료가 없습니다.")

    st.divider()

    st.markdown("### 🛒 장보기 필요 목록")

    shopping = purchase_list()

    if shopping:
        st.dataframe(
            pd.DataFrame(shopping),
            use_container_width=True,
            hide_index=True,
        )

        total = sum(row["예상 비용"] for row in shopping)
        st.write(f"예상 구매 비용: **{won(total)}**")
    else:
        st.info("현재 최소 보유량 기준으로 구매할 식재료가 없습니다.")

    st.markdown("### 📦 전체 재고")

    if st.session_state.inventory:
        st.dataframe(
            inventory_dataframe(),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("등록된 식재료가 없습니다. 재고 관리 메뉴에서 추가하세요.")


# ==================================================
# 6. AI 재고 분석
# ==================================================
elif page == "AI 재고 분석":
    st.subheader("🤖 AI 재고 분석")
    st.write(
        "현재 재고, 최소 보유량, 유통기한을 바탕으로 "
        "식재료 관리 방법을 분석합니다."
    )

    if st.button("AI 재고 분석 시작", type="primary"):
        inventory_text = format_inventory_for_ai()

        prompt = f"""
너는 소규모 식당을 돕는 주방 재고 관리 AI야.

아래 재고 정보를 분석해서 한국어로 답변해 줘.

1. 재고가 부족한 식재료
2. 유통기한이 가까운 식재료
3. 먼저 사용하거나 확인해야 할 식재료
4. 재고 낭비를 줄이는 실천 방법
5. 오늘 관리자가 할 일 3가지

식재료의 수량이나 유통기한을 임의로 만들어 내지 마.
유통기한이 지났다면 실제 사용 가능 여부를 단정하지 말고
안전하게 상태를 확인하도록 안내해.

[현재 날짜]
{TODAY}

[재고 정보]
{inventory_text}
"""
        with st.spinner("AI가 재고를 분석하고 있습니다..."):
            st.session_state.ai_stock_result = ask_gemini(prompt)

    if st.session_state.ai_stock_result:
        st.markdown("### 분석 결과")
        st.markdown(st.session_state.ai_stock_result)


# ==================================================
# 7. 재고 관리
# ==================================================
elif page == "재고 관리":
    st.subheader("📦 재고 관리")

    st.markdown("### 현재 재고 목록")

    if st.session_state.inventory:
        st.dataframe(
            inventory_dataframe(),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("등록된 식재료가 없습니다.")

    st.divider()

    st.markdown("### 식재료 추가")

    with st.form("add_inventory_form", clear_on_submit=True):
        new_name = st.text_input("식재료 이름")
        c1, c2, c3 = st.columns(3)

        with c1:
            new_qty = st.number_input(
                "현재 수량",
                min_value=0.0,
                value=1.0,
                step=1.0,
            )

        with c2:
            new_unit = st.selectbox(
                "단위",
                ["개", "kg", "g", "L", "팩", "모", "대", "봉"],
            )

        with c3:
            new_minimum = st.number_input(
                "최소 보유량",
                min_value=0.0,
                value=1.0,
                step=1.0,
            )

        c4, c5 = st.columns(2)

        with c4:
            new_price = st.number_input(
                "단위당 가격(원)",
                min_value=0,
                value=1000,
                step=100,
            )

        with c5:
            new_expiry = st.date_input(
                "유통기한",
                value=TODAY + timedelta(days=7),
            )

        add_submitted = st.form_submit_button("식재료 추가")

    if add_submitted:
        clean_name = new_name.strip()

        if not clean_name:
            st.error("식재료 이름을 입력하세요.")
        elif get_item(clean_name):
            st.error("같은 이름의 식재료가 이미 있습니다.")
        else:
            st.session_state.inventory.append({
                "name": clean_name,
                "qty": float(new_qty),
                "unit": new_unit,
                "minimum": float(new_minimum),
                "price": int(new_price),
                "expiry": new_expiry,
            })
            st.success(f"{clean_name} 재고를 추가했습니다.")
            st.rerun()

    st.divider()

    st.markdown("### 식재료 정보 수정")

    inventory_names = [
        item["name"] for item in st.session_state.inventory
    ]

    if inventory_names:
        selected_name = st.selectbox(
            "수정할 식재료",
            inventory_names,
            key="edit_inventory_name",
        )

        selected_item = get_item(selected_name)

        if selected_item:
            with st.form("edit_inventory_form"):
                edit_qty = st.number_input(
                    "현재 수량",
                    min_value=0.0,
                    value=float(selected_item["qty"]),
                    step=1.0,
                )

                edit_minimum = st.number_input(
                    "최소 보유량",
                    min_value=0.0,
                    value=float(selected_item["minimum"]),
                    step=1.0,
                )

                edit_price = st.number_input(
                    "단위당 가격(원)",
                    min_value=0,
                    value=int(selected_item["price"]),
                    step=100,
                )

                edit_expiry = st.date_input(
                    "유통기한",
                    value=selected_item["expiry"],
                )

                edit_submitted = st.form_submit_button("변경사항 저장")

            if edit_submitted:
                selected_item["qty"] = float(edit_qty)
                selected_item["minimum"] = float(edit_minimum)
                selected_item["price"] = int(edit_price)
                selected_item["expiry"] = edit_expiry

                st.success(f"{selected_name} 정보를 수정했습니다.")
                st.rerun()

        st.divider()

        st.markdown("### 식재료 삭제")

        delete_name = st.selectbox(
            "삭제할 식재료",
            inventory_names,
            key="delete_inventory_name",
        )

        if st.button("선택한 식재료 삭제", type="secondary"):
            st.session_state.inventory = [
                item
                for item in st.session_state.inventory
                if item["name"] != delete_name
            ]

            st.warning(f"{delete_name} 식재료를 삭제했습니다.")
            st.rerun()
    else:
        st.info("수정하거나 삭제할 식재료가 없습니다.")


# ==================================================
# 8. 유통기한 관리
# ==================================================
elif page == "유통기한 관리":
    st.subheader("⏰ 유통기한 관리")

    days_filter = st.selectbox(
        "확인할 기간",
        [1, 3, 7, 14, 30],
        index=2,
        format_func=lambda x: f"앞으로 {x}일 이내 + 기한이 지난 식재료",
    )

    expiry_items = expiring_soon(days_filter)

    if expiry_items:
        for item, days in expiry_items:
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 3])

                c1.markdown(f"**{item['name']}**")
                c1.write(f"수량: {item['qty']} {item['unit']}")
                c2.write(f"유통기한: {item['expiry']}")

                if days < 0:
                    c3.error(f"유통기한 {abs(days)}일 지남")
                elif days == 0:
                    c3.warning("유통기한이 오늘까지입니다.")
                else:
                    c3.warning(f"유통기한까지 {days}일 남았습니다.")

                st.caption(
                    "유통기한이 지났거나 상태가 의심스러운 식재료는 "
                    "안전성을 확인하고, 문제가 있으면 사용하지 마세요."
                )
    else:
        st.success("선택한 기간에 해당하는 식재료가 없습니다.")

    st.divider()
    st.markdown("### 전체 식재료 유통기한")

    if st.session_state.inventory:
        expiry_df = pd.DataFrame([
            {
                "식재료": item["name"],
                "수량": f"{item['qty']} {item['unit']}",
                "유통기한": item["expiry"].isoformat(),
                "남은 일수": (item["expiry"] - TODAY).days,
            }
            for item in st.session_state.inventory
        ])

        st.dataframe(
            expiry_df.sort_values("남은 일수"),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("등록된 식재료가 없습니다.")


# ==================================================
# 9. AI 장보기 추천
# ==================================================
elif page == "AI 장보기 추천":
    st.subheader("🛒 AI 장보기 추천")
    st.write(
        "현재 재고와 최소 보유량을 기준으로 필요한 식재료를 확인하고 "
        "AI에게 구매 우선순위와 관리 팁을 요청합니다."
    )

    shopping = purchase_list()

    if shopping:
        st.markdown("### 자동 계산된 구매 목록")

        shopping_df = pd.DataFrame(shopping)
        st.dataframe(
            shopping_df,
            use_container_width=True,
            hide_index=True,
        )

        total_cost = sum(row["예상 비용"] for row in shopping)
        st.metric("예상 구매 비용", won(total_cost))
    else:
        st.success(
            "최소 보유량보다 부족한 식재료가 없습니다. "
            "필요하면 재고 관리에서 최소 보유량을 조정하세요."
        )

    st.divider()

    st.markdown("### AI 추천")

    if st.button("AI 장보기 추천 받기", type="primary"):
        inventory_text = format_inventory_for_ai()

        if shopping:
            shopping_text = "\n".join(
                f"- {row['식재료']}: {row['구매 필요 수량']} "
                f"{row['단위']} 구매 필요"
                for row in shopping
            )
        else:
            shopping_text = "현재 최소 보유량 기준 부족한 식재료가 없습니다."

        prompt = f"""
너는 식당의 식재료 구매를 돕는 AI야.

아래 정보를 바탕으로 한국어로 장보기 계획을 작성해 줘.

1. 구매 우선순위
2. 먼저 구매할 식재료와 필요한 수량
3. 식재료 낭비를 줄이는 방법
4. 재고 관리자가 오늘 확인할 사항

구매 수량은 아래 자동 계산 목록을 우선으로 사용해.
정보에 없는 가격이나 재고 수량은 사실처럼 만들지 마.
유통기한이 지난 식재료는 무조건 사용하라고 권하지 마.

[오늘 날짜]
{TODAY}

[현재 재고]
{inventory_text}

[자동 계산 구매 목록]
{shopping_text}
"""
        with st.spinner("AI가 장보기 계획을 작성하고 있습니다..."):
            st.session_state.ai_shopping_result = ask_gemini(prompt)

    if st.session_state.ai_shopping_result:
        st.markdown("### AI 장보기 계획")
        st.markdown(st.session_state.ai_shopping_result)

    st.divider()

    st.markdown("### 구매 완료 후 재고 반영")

    if st.session_state.inventory:
        purchase_name = st.selectbox(
            "구매한 식재료",
            [item["name"] for item in st.session_state.inventory],
        )

        purchase_item = get_item(purchase_name)

        if purchase_item:
            purchase_qty = st.number_input(
                f"추가할 수량 ({purchase_item['unit']})",
                min_value=0.0,
                value=1.0,
                step=1.0,
                key="purchase_qty_input",
            )

            if st.button("구매한 수량 재고에 추가"):
                if purchase_qty <= 0:
                    st.error("추가할 수량은 0보다 커야 합니다.")
                else:
                    purchase_item["qty"] += float(purchase_qty)
                    st.success(
                        f"{purchase_name} 재고를 "
                        f"{purchase_qty} {purchase_item['unit']}만큼 추가했습니다."
                    )
                    st.rerun()


# ==================================================
# 10. 주문 관리
# ==================================================
elif page == "주문 관리":
    st.subheader("🍱 주문 관리")
    st.write(
        "메뉴와 수량을 등록한 다음, 실제 음식 제공이 끝났을 때 "
        "완료 버튼을 눌러 주세요. 완료된 주문만 재고에서 차감됩니다."
    )

    st.caption(
        "기본 레시피는 예시입니다. 실제 식당에서 사용하는 양에 맞게 "
        "아래 RECIPES의 수치를 수정하세요."
    )

    st.markdown("### 메뉴별 기본 레시피")

    recipe_rows = []

    for menu, ingredients in RECIPES.items():
        for ingredient_name, amount in ingredients.items():
            item = get_item(ingredient_name)
            unit = item["unit"] if item else "(재고 미등록)"

            recipe_rows.append({
                "메뉴": menu,
                "식재료": ingredient_name,
                "1인분 사용량": amount,
                "단위": unit,
            })

    st.dataframe(
        pd.DataFrame(recipe_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.markdown("### 새 주문 등록")

    with st.form("new_order_form", clear_on_submit=True):
        menu_choice = st.selectbox("메뉴", list(RECIPES.keys()))
        order_quantity = st.number_input(
            "주문 수량",
            min_value=1,
            max_value=1000,
            value=1,
            step=1,
        )
        order_note = st.text_input("요청사항 (선택)")

        order_submitted = st.form_submit_button("주문 등록")

    if order_submitted:
        order_id = st.session_state.next_order_id

        st.session_state.orders.append({
            "id": order_id,
            "menu": menu_choice,
            "quantity": int(order_quantity),
            "note": order_note.strip(),
            "status": "조리 대기",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

        st.session_state.next_order_id += 1
        st.success(f"주문 #{order_id} 등록이 완료되었습니다.")
        st.rerun()

    st.divider()
    st.markdown("### 주문 목록")

    if not st.session_state.orders:
        st.info("등록된 주문이 없습니다.")
    else:
        for order in reversed(st.session_state.orders):
            with st.container(border=True):
                st.markdown(
                    f"**주문 #{order['id']} · {order['menu']} "
                    f"× {order['quantity']}**"
                )

                st.write(f"등록 시각: {order['created_at']}")
                st.write(f"상태: {order['status']}")

                if order["note"]:
                    st.write(f"요청사항: {order['note']}")

                ingredients = RECIPES[order["menu"]]

                st.markdown("**필요한 식재료**")

                required = {}
                for ingredient_name, amount in ingredients.items():
                    required[ingredient_name] = amount * order["quantity"]

                for ingredient_name, amount in required.items():
                    item = get_item(ingredient_name)

                    if item is None:
                        st.error(
                            f"{ingredient_name}: 재고에 등록되지 않았습니다."
                        )
                    else:
                        st.write(
                            f"- {ingredient_name}: {amount:g} {item['unit']} "
                            f"(현재 재고 {item['qty']:g} {item['unit']})"
                        )

                if order["status"] != "제공 완료":
                    if st.button(
                        f"주문 #{order['id']} 음식 제공 완료 · 재고 차감",
                        key=f"complete_order_{order['id']}",
                        type="primary",
                    ):
                        missing = []
                        insufficient = []

                        # 먼저 모든 식재료가 있는지와 수량이 충분한지 확인
                        for ingredient_name, amount in required.items():
                            item = get_item(ingredient_name)

                            if item is None:
                                missing.append(ingredient_name)
                            elif item["qty"] < amount:
                                insufficient.append(
                                    f"{ingredient_name} "
                                    f"(필요 {amount:g}, 현재 {item['qty']:g})"
                                )

                        if missing:
                            st.error(
                                "재고에 등록되지 않은 식재료가 있어 차감할 수 없습니다: "
                                + ", ".join(missing)
                            )
                        elif insufficient:
                            st.error(
                                "재고가 부족하여 주문을 완료할 수 없습니다: "
                                + ", ".join(insufficient)
                            )
                        else:
                            # 모든 재고를 확인한 후 한 번에 차감
                            for ingredient_name, amount in required.items():
                                item = get_item(ingredient_name)
                                item["qty"] -= amount

                            order["status"] = "제공 완료"

                            st.success(
                                f"주문 #{order['id']} 완료! "
                                "사용한 식재료를 재고에서 차감했습니다."
                            )
                            st.rerun()
                else:
                    st.success("이 주문은 이미 완료되어 재고 차감이 끝났습니다.")

    st.divider()
    st.markdown("### 현재 재고 및 구매 필요 목록")

    if st.session_state.inventory:
        st.dataframe(
            inventory_dataframe(),
            use_container_width=True,
            hide_index=True,
        )

    shopping = purchase_list()

    if shopping:
        st.markdown("**현재 구매가 필요한 식재료**")
        st.dataframe(
            pd.DataFrame(shopping),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("최소 보유량 기준으로 추가 구매가 필요한 식재료가 없습니다.")


# ==================================================
# 11. 예약 통합 관리
# ==================================================
elif page == "예약 통합 관리":
    st.subheader("📅 예약 통합 관리")
    st.write("전화, 방문 등으로 접수한 예약을 한곳에서 관리합니다.")

    st.markdown("### 새 예약 등록")

    with st.form("new_reservation_form", clear_on_submit=True):
        guest_name = st.text_input("예약자 이름")
        c1, c2 = st.columns(2)

        with c1:
            guest_count = st.number_input(
                "인원수",
                min_value=1,
                max_value=100,
                value=2,
                step=1,
            )

            reservation_day = st.date_input(
                "예약 날짜",
                value=TODAY,
                min_value=TODAY,
            )

        with c2:
            reservation_time = st.time_input(
                "예약 시간",
                value=time(18, 0),
            )

            reservation_channel = st.selectbox(
                "예약 접수 경로",
                ["전화", "방문", "온라인", "기타"],
            )

        reservation_memo = st.text_input("요청사항 (선택)")

        reservation_submitted = st.form_submit_button("예약 등록")

    if reservation_submitted:
        clean_guest_name = guest_name.strip()

        if not clean_guest_name:
            st.error("예약자 이름을 입력하세요.")
        else:
            reservation_id = st.session_state.next_reservation_id

            st.session_state.reservations.append({
                "id": reservation_id,
                "name": clean_guest_name,
                "guests": int(guest_count),
                "day": reservation_day,
                "time": reservation_time.strftime("%H:%M"),
                "channel": reservation_channel,
                "status": "예약 확정",
                "memo": reservation_memo.strip(),
            })

            st.session_state.next_reservation_id += 1
            st.success(f"예약 #{reservation_id} 등록이 완료되었습니다.")
            st.rerun()

    st.divider()
    st.markdown("### 예약 목록")

    if not st.session_state.reservations:
        st.info("등록된 예약이 없습니다.")
    else:
        sorted_reservations = sorted(
            st.session_state.reservations,
            key=lambda x: (x["day"], x["time"]),
        )

        for reservation in sorted_reservations:
            with st.container(border=True):
                st.markdown(
                    f"**예약 #{reservation['id']} · "
                    f"{reservation['name']} · "
                    f"{reservation['guests']}명**"
                )

                st.write(
                    f"예약 일시: {reservation['day']} "
                    f"{reservation['time']}"
                )
                st.write(f"접수 경로: {reservation['channel']}")
                st.write(f"현재 상태: {reservation['status']}")

                if reservation["memo"]:
                    st.write(f"요청사항: {reservation['memo']}")

                status_options = [
                    "예약 확정",
                    "방문 완료",
                    "취소",
                ]

                current_status_index = status_options.index(
                    reservation["status"]
                )

                new_status = st.selectbox(
                    "예약 상태 변경",
                    status_options,
                    index=current_status_index,
                    key=f"reservation_status_{reservation['id']}",
                )

                c1, c2 = st.columns(2)

                with c1:
                    if st.button(
                        f"상태 저장 #{reservation['id']}",
                        key=f"save_reservation_{reservation['id']}",
                    ):
                        reservation["status"] = new_status
                        st.success("예약 상태를 변경했습니다.")
                        st.rerun()

                with c2:
                    if st.button(
                        f"예약 삭제 #{reservation['id']}",
                        key=f"delete_reservation_{reservation['id']}",
                    ):
                        st.session_state.reservations = [
                            r for r in st.session_state.reservations
                            if r["id"] != reservation["id"]
                        ]
                        st.warning("예약을 삭제했습니다.")
                        st.rerun()


# ==================================================
# 12. 하단 안내
# ==================================================
st.divider()

st.caption(
    "AI 주방매니저 시제품 | 재고·주문·예약 데이터는 현재 세션에 저장됩니다. "
    "앱 재시작이나 세션 초기화 시 데이터가 사라질 수 있습니다."
)
