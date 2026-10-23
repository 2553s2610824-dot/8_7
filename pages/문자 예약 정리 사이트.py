        hour, minute = int(time_match.group(1)), int(time_match.group(2))
    else:
        time_match = re.search(r"(?<!\d)([01]?\d|2[0-3])\s*시(?:\s*([0-5]?\d)\s*분?)?", text)
        if not time_match:
            return None, "예약 시간을 찾지 못했어요. 예: 18:30 또는 18시 30분"
        hour, minute = int(time_match.group(1)), int(time_match.group(2) or 0)

    food_match = re.search(r"(?:음식|메뉴)\s*[:：=]\s*([^\n]+)", text)
    if food_match:
        food_text = food_match.group(1).strip()
    else:
        # '2명, 18:30, 삼겹살 2인분, 된장찌개 1개' 형태도 지원합니다.
        food_text = re.sub(r"\d+\s*명", " ", text)
        food_text = re.sub(r"(?<!\d)([01]?\d|2[0-3])\s*:\s*[0-5]\d(?!\d)", " ", food_text)
        food_text = re.sub(r"(?<!\d)([01]?\d|2[0-3])\s*시(?:\s*[0-5]?\d\s*분?)?", " ", food_text)
        food_text = re.sub(r"(?:인원수?|시간)\s*[:：=]?", " ", food_text)
        food_text = re.sub(r"^[,，/|\s]+|[,，/|\s]+$", "", food_text)
        # 앞쪽의 예약 인원/시간 뒤에 오는 구분 기호만 제거하고 메뉴 내부 쉼표는 유지합니다.
        food_text = re.sub(r"^\s*[,，/|]+\s*", "", food_text)
        food_text = re.sub(r"\s+", " ", food_text).strip(" -·")

    food_items = parse_food_items(food_text)
    if not food_items:
        return None, "음식 종류를 찾지 못했어요. 예: 음식: 삼겹살 2인분, 된장찌개 1개"

    return {
        "people": people,
        "hour": hour,
        "minute": minute,
        "food": food_text,
        "food_items": food_items,
        "datetime": datetime.combine(date.today(), time(hour, minute)),
        "raw": raw_text.strip(),
        "created": datetime.now().isoformat(timespec="seconds"),
    }, None


left, right = st.columns([0.92, 1.08], gap="large")

with left:
    with st.container(border=True):
        st.markdown('<div class="panel-heading">✍️ 예약 문자 입력</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">메시지를 복사해 붙여 넣고 채널을 선택하세요.</div>', unsafe_allow_html=True)
        source = st.selectbox("연락이 들어온 앱", list(SOURCE_STYLES.keys()))
        raw_text = st.text_area(
            "예약 내용",
            height=190,
            placeholder="예시: 4명, 18:30, 삼겹살 2인분, 된장찌개 1개\n\n또는\n인원: 4명 / 시간: 18:30 / 음식: 삼겹살 2인분, 된장찌개 1개",
            help="인원수, 예약 시간, 음식 종류를 포함한 문자를 붙여 넣어 주세요.",
        )
        if st.button("＋  예약 추가", type="primary", width="stretch"):
            reservation, error = parse_reservation(raw_text)
            if error:
                st.error(error)
            else:
                reservation["source"] = source
                reservation["id"] = reservation["created"]
                st.session_state.reservations.append(reservation)
                st.toast("예약을 추가했어요!", icon="✅")
                st.rerun()

        st.markdown("**입력 예시**")
        st.code("4명, 18:30, 삼겹살 2인분, 된장찌개 1개", language="text")
        st.code("인원: 2명 / 시간: 19:00 / 음식: 파스타 2개, 콜라 2잔", language="text")
        st.markdown('<div class="small-note">카카오톡=노랑 · 인스타그램=보라 · 문자=파랑</div>', unsafe_allow_html=True)

with right:
    with st.container(border=True):
        st.markdown('<div class="panel-heading">🗂️ 예약 정리표</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">이 영역 안에서 마우스 휠로 예약 목록만 스크롤할 수 있어요.</div>', unsafe_allow_html=True)

        reservations = sorted(
            st.session_state.reservations,
            key=lambda item: (item["datetime"] < datetime.now(), item["datetime"]),
        )
        total_people = sum(item["people"] for item in reservations)
        total_menu_kinds = sum(len(item.get("food_items", [])) for item in reservations)
        m1, m2, m3 = st.columns(3)
        m1.metric("등록된 예약", f"{len(reservations)}건")
        m2.metric("예약 인원", f"{total_people}명")
        m3.metric("메뉴 종류", f"{total_menu_kinds}종")

        # 고정 높이 컨테이너이므로 예약이 많아도 오른쪽 목록만 스크롤됩니다.
        with st.container(height=570, border=False):
            if reservations:
                for item in reservations:
                    style = SOURCE_STYLES[item["source"]]
                    time_label = f'{item["hour"]:02d}:{item["minute"]:02d}'
                    past = item["datetime"] < datetime.now()
                    status = "지난 시간" if past else "예정"
                    food_rows = "".join(
                        f'''<div class="food-row">
                            <div class="food-icon">{menu["emoji"]}</div>
                            <div class="food-name">{menu["name"]}</div>
                            <div class="food-quantity">{menu["quantity"]}</div>
                        </div>'''
                        for menu in item.get("food_items", [{"name": item["food"], "emoji": "🍽️", "quantity": ""}])
                    )
                    menu_count = len(item.get("food_items", []))
                    st.markdown(
                        f'''<div class="reservation-card" style="--card-bg:{style["bg"]}; --card-border:{style["border"]};">
                            <div class="reservation-top">
                                <div class="reservation-time">{time_label}</div>
                                <div class="reservation-people">{item["people"]}명 · {status}</div>
                            </div>
                            <div class="menu-count">🍽️ 메뉴 {menu_count}종</div>
                            {food_rows}
                            <div class="reservation-source">{style["emoji"]} {item["source"]}</div>
                        </div>''',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="empty-state"><div class="empty-icon">🗓️</div><b>아직 등록된 예약이 없어요.</b><br>왼쪽에서 예약 문자를 입력해 추가해 주세요.</div>',
                    unsafe_allow_html=True,
                )

        if reservations and st.button("🗑️ 전체 예약 삭제", width="stretch"):
            st.session_state.reservations = []
            st.rerun()
