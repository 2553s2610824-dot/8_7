import streamlit as st
from datetime import date, timedelta

st.set_page_config(
    page_title="스마트 키친 | 메인",
    page_icon="🍳",
    layout="wide",
)

# ---------- 디자인 ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #edf2f8, #dce6f1, #eef3f8);
    color: #1e293b;
}
.block-container {
    padding-top: 1.8rem;
    max-width: 1250px;
}
.hero {
    background: rgba(255,255,255,.9);
    border-radius: 24px;
    padding: 26px 30px;
    margin-bottom: 20px;
    box-shadow: 0 8px 28px rgba(31,41,55,.07);
}
.hero h1 {color:#1e293b; margin:0;}
.hero p {color:#64748b;}
.panel {
    background: rgba(255,255,255,.92);
    border-radius: 20px;
    padding: 21px;
    box-shadow: 0 7px 24px rgba(31,41,55,.06);
    margin-bottom: 12px;
    min-height: 145px;
}
.metric {
    font-size: 2rem;
    font-weight: 800;
    color: #315b78;
}
.muted {color:#64748b; font-size:.9rem;}
.notice {
    background:#fff7e8;
    border-left:5px solid #f0ad4e;
    padding:12px 15px;
    border-radius:10px;
    margin:8px 0;
    color:#7c5418;
}
div.stButton > button {
    border-radius:12px;
    min-height:44px;
    font-weight:600;
}
[data-testid="stSidebar"] {
    background:#f8fafc;
}
</style>
""", unsafe_allow_html=True)

# ---------- 기본 데이터 ----------
if "ingredients" not in st.session_state:
    today = date.today()
    st.session_state.ingredients = [
        {"name":"우유", "quantity":2, "unit":"개",
         "expiry":today+timedelta(days=1), "category":"유제품"},
        {"name":"달걀", "quantity":10, "unit":"개",
         "expiry":today+timedelta(days=4), "category":"유제품"},
        {"name":"양파", "quantity":3, "unit":"개",
         "expiry":today+timedelta(days=8), "category":"채소"},
        {"name":"두부", "quantity":1, "unit":"모",
         "expiry":today, "category":"기타"},
        {"name":"토마토", "quantity":4, "unit":"개",
         "expiry":today+timedelta(days=2), "category":"채소"},
    ]

if "completed_tasks" not in st.session_state:
    st.session_state.completed_tasks = []

today = date.today()
ingredients = st.session_state.ingredients

expiring = [
    x for x in ingredients
    if (x["expiry"] - today).days <= 3
]
low_stock = [x for x in ingredients if x["quantity"] <= 2]

# ---------- 사이드 메뉴 ----------
with st.sidebar:
    st.markdown("## 🍳 스마트 키친")
    st.caption("SMART KITCHEN DASHBOARD")
    page = st.radio(
        "메뉴 선택",
        ["메인 페이지", "식재료 관리", "유통기한 확인", "오늘의 메뉴"]
    )
    st.divider()
    st.caption("식재료 정보는 시연용 예시 데이터입니다.")

# ---------- 메인 페이지 ----------
if page == "메인 페이지":

    st.markdown(f"""
    <div class="hero">
        <p>SMART KITCHEN DASHBOARD</p>
        <h1>우리 집 주방을 한눈에 🏡</h1>
        <p>{today.strftime('%Y년 %m월 %d일')} ·
        식재료를 확인하고 더 똑똑하게 관리해 보세요.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        ("🧺 등록된 식재료", f"{len(ingredients)}종", "현재 목록 기준"),
        ("⏰ 유통기한 임박", f"{len(expiring)}종", "3일 이내 또는 지난 식재료"),
        ("📦 재고 확인 필요", f"{len(low_stock)}종", "수량 2개 이하"),
        ("✅ 오늘의 체크",
         f"{len(st.session_state.completed_tasks)}/3",
         "주방 관리 체크리스트"),
    ]

    for col, (title, value, desc) in zip(
        [c1, c2, c3, c4], cards
    ):
        with col:
            st.markdown(f"""
            <div class="panel">
                <h4>{title}</h4>
                <div class="metric">{value}</div>
                <div class="muted">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.subheader("🔔 먼저 확인할 식재료")

        if not expiring:
            st.success("유통기한이 임박한 식재료가 없습니다.")
        else:
            for item in sorted(expiring, key=lambda x: x["expiry"]):
                days = (item["expiry"] - today).days

                if days < 0:
                    msg = f"유통기한 {abs(days)}일 지남"
                elif days == 0:
                    msg = "오늘까지"
                else:
                    msg = f"{days}일 남음"

                st.markdown(
                    f'<div class="notice">⚠️ '
                    f'<b>{item["name"]}</b> · {msg}</div>',
                    unsafe_allow_html=True
                )

        st.subheader("📦 식재료 재고 현황")

        if ingredients:
            st.dataframe(
                [
                    {
                        "식재료": x["name"],
                        "수량": f'{x["quantity"]} {x["unit"]}',
                        "유통기한": x["expiry"].isoformat(),
                    }
                    for x in ingredients
                ],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("등록된 식재료가 없습니다.")

    with right:
        st.subheader("📝 오늘의 주방 체크리스트")

        tasks = [
            "냉장고 유통기한 확인하기",
            "부족한 식재료 확인하기",
            "오늘 먹을 메뉴 정하기",
        ]

        for task in tasks:
            checked = st.checkbox(
                task,
                value=task in st.session_state.completed_tasks,
                key=f"check_{task}",
            )

            if checked and task not in st.session_state.completed_tasks:
                st.session_state.completed_tasks.append(task)
            elif not checked and task in st.session_state.completed_tasks:
                st.session_state.completed_tasks.remove(task)

        st.progress(
            len(st.session_state.completed_tasks) / len(tasks)
        )
        st.caption(
            f"완료: {len(st.session_state.completed_tasks)} / {len(tasks)}"
        )

        st.subheader("🍽️ 오늘의 메뉴 아이디어")

        st.markdown("""
        <div class="panel">
            <h3>🍅 토마토 달걀볶음</h3>
            <p>달걀과 토마토를 활용한 간단한 메뉴예요.</p>
            <p>① 토마토를 먹기 좋게 자르기</p>
            <p>② 달걀을 먼저 익히기</p>
            <p>③ 토마토를 넣고 함께 볶기</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("🚀 빠른 메뉴")

    q1, q2, q3 = st.columns(3)

    with q1:
        if st.button("🧺 식재료 관리", use_container_width=True):
            st.session_state["selected_page"] = "식재료 관리"
            st.rerun()

    with q2:
        if st.button("⏰ 유통기한 확인", use_container_width=True):
            st.session_state["selected_page"] = "유통기한 확인"
            st.rerun()

    with q3:
        if st.button("🍽️ 오늘의 메뉴", use_container_width=True):
            st.session_state["selected_page"] = "오늘의 메뉴"
            st.rerun()

# ---------- 식재료 관리 ----------
elif page == "식재료 관리":

    st.markdown("""
    <div class="hero">
        <h1>🧺 식재료 관리</h1>
        <p>식재료를 등록하고 수량과 유통기한을 관리하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("add_ingredient", clear_on_submit=True):
        name = st.text_input("식재료 이름", placeholder="예: 당근")

        c1, c2, c3 = st.columns(3)

        with c1:
            quantity = st.number_input(
                "수량", min_value=0, max_value=10000, value=1
            )

        with c2:
            unit = st.selectbox(
                "단위", ["개", "봉", "팩", "병", "모", "g", "kg", "L"]
            )

        with c3:
            expiry = st.date_input(
                "유통기한", value=today + timedelta(days=7)
            )

        category = st.selectbox(
            "분류",
            ["채소", "과일", "유제품", "육류·해산물", "곡류", "기타"]
        )

        submitted = st.form_submit_button("➕ 식재료 등록")

        if submitted:
            if not name.strip():
                st.error("식재료 이름을 입력해 주세요.")
            elif any(
                x["name"].casefold() == name.strip().casefold()
                for x in ingredients
            ):
                st.warning("이미 등록된 식재료입니다.")
            else:
                st.session_state.ingredients.append({
                    "name": name.strip(),
                    "quantity": int(quantity),
                    "unit": unit,
                    "expiry": expiry,
                    "category": category,
                })
                st.success("식재료가 등록되었습니다.")
                st.rerun()

    st.subheader("등록된 식재료")

    if not ingredients:
        st.info("등록된 식재료가 없습니다.")

    for idx, item in enumerate(list(ingredients)):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 1, 1.5, 1])

            with c1:
                st.write(f"**{item['name']}**")
                st.caption(item["category"])

            with c2:
                st.write(f"{item['quantity']} {item['unit']}")

            with c3:
                days = (item["expiry"] - today).days

                if days < 0:
                    st.error(f"{abs(days)}일 지남")
                elif days == 0:
                    st.warning("오늘까지")
                else:
                    st.write(f"{days}일 남음")

                st.caption(item["expiry"].isoformat())

            with c4:
                if st.button("삭제", key=f"delete_{idx}"):
                    st.session_state.ingredients.pop(idx)
                    st.rerun()

# ---------- 유통기한 확인 ----------
elif page == "유통기한 확인":

    st.markdown("""
    <div class="hero">
        <h1>⏰ 유통기한 확인</h1>
        <p>유통기한을 기준으로 식재료를 확인하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    choice = st.selectbox(
        "표시할 항목",
        ["전체", "유통기한 지남", "오늘까지", "3일 이내", "4일 이상 남음"],
    )

    shown = []

    for item in ingredients:
        days = (item["expiry"] - today).days

        if choice == "전체":
            shown.append(item)
        elif choice == "유통기한 지남" and days < 0:
            shown.append(item)
        elif choice == "오늘까지" and days == 0:
            shown.append(item)
        elif choice == "3일 이내" and 0 <= days <= 3:
            shown.append(item)
        elif choice == "4일 이상 남음" and days >= 4:
            shown.append(item)

    if not shown:
        st.info("선택한 조건에 해당하는 식재료가 없습니다.")

    for item in sorted(shown, key=lambda x: x["expiry"]):
        days = (item["expiry"] - today).days

        if days < 0:
            st.error(f"🔴 {item['name']} — 유통기한 {abs(days)}일 지남")
        elif days == 0:
            st.warning(f"🟠 {item['name']} — 설정된 날짜가 오늘입니다.")
        elif days <= 3:
            st.warning(f"🟡 {item['name']} — {days}일 남음")
        else:
            st.success(f"🟢 {item['name']} — {days}일 남음")

# ---------- 오늘의 메뉴 ----------
elif page == "오늘의 메뉴":

    st.markdown("""
    <div class="hero">
        <h1>🍽️ 오늘의 메뉴</h1>
        <p>보유한 식재료를 활용할 수 있는 메뉴를 확인하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    available = {
        x["name"].strip().casefold()
        for x in ingredients if x["quantity"] > 0
    }

    menus = [
        {
            "name": "토마토 달걀볶음",
            "items": ["토마토", "달걀"],
            "description": "토마토와 달걀을 함께 볶는 간단한 메뉴예요.",
        },
        {
            "name": "두부 양파볶음",
            "items": ["두부", "양파"],
            "description": "두부와 양파를 활용한 간단한 반찬이에요.",
        },
        {
            "name": "달걀 양파전",
            "items": ["달걀", "양파"],
            "description": "달걀과 양파를 섞어 부치는 메뉴예요.",
        },
    ]

    for menu in menus:
        matches = [
            x for x in menu["items"] if x.casefold() in available
        ]
        missing = [
            x for x in menu["items"] if x.casefold() not in available
        ]

        with st.container(border=True):
            st.subheader(menu["name"])
            st.write(menu["description"])
            st.caption("필요한 재료: " + ", ".join(menu["items"]))

            if not missing:
                st.success("등록된 재료를 모두 보유하고 있어요.")
            elif matches:
                st.info(
                    "보유 재료: " + ", ".join(matches)
                    + " · 추가 필요: " + ", ".join(missing)
                )
            else:
                st.caption("추가 필요: " + ", ".join(missing))

st.divider()
st.caption(
    "Smart Kitchen · 시연용 앱 | "
    "실제 식재료의 상태와 안전성은 별도로 확인하세요."
)
