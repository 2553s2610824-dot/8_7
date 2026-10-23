
import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(
    page_title="전화 · 매출 관리",
    page_icon="☎️",
    layout="wide",
)

DB_PATH = "calls.db"

CALL_CATEGORIES = ["문의", "예약", "주문", "불만", "업무", "기타"]
CALL_STATUSES = ["미처리", "처리 중", "완료"]


# -------------------------
# 데이터베이스
# -------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_time TEXT NOT NULL,
                caller TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date TEXT NOT NULL,
                product TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price INTEGER NOT NULL CHECK(unit_price >= 0),
                note TEXT NOT NULL DEFAULT ''
            )
        """)


def add_call(caller, phone, category, summary, status):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO calls
            (call_time, caller, phone, category, summary, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            caller.strip(),
            phone.strip(),
            category,
            summary.strip(),
            status,
        ))


def add_sale(sale_date, product, quantity, unit_price, note):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO sales
            (sale_date, product, quantity, unit_price, note)
            VALUES (?, ?, ?, ?, ?)
        """, (
            sale_date.isoformat(),
            product.strip(),
            int(quantity),
            int(unit_price),
            note.strip(),
        ))


def load_calls():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM calls ORDER BY id DESC", conn
        )


def load_sales():
    with get_connection() as conn:
        return pd.read_sql_query("""
            SELECT id, sale_date, product, quantity, unit_price,
                   quantity * unit_price AS total, note
            FROM sales
            ORDER BY sale_date DESC, id DESC
        """, conn)


# 데이터베이스 초기화
try:
    init_db()
except (sqlite3.Error, OSError):
    st.error(
        "데이터베이스를 준비하지 못했습니다. "
        "저장 경로와 파일 권한을 확인해 주세요."
    )
    st.stop()


# -------------------------
# 앱 제목과 메뉴
# -------------------------
st.title("☎️ 전화 · 매출 관리")
st.caption("전화 기록과 매출을 한곳에서 관리하는 대시보드")

page = st.sidebar.radio(
    "메뉴",
    ["대시보드", "전화 기록", "매출 관리"],
)

st.sidebar.caption("대시보드는 5초마다 기록을 새로 불러옵니다.")


# -------------------------
# 전화 기록 입력
# -------------------------
def call_entry_form():
    with st.expander("➕ 새 전화 기록 추가", expanded=True):
        with st.form("call_form", clear_on_submit=True):
            caller = st.text_input("발신자 이름")
            phone = st.text_input("전화번호")
            category = st.selectbox(
                "전화 유형", CALL_CATEGORIES
            )
            summary = st.text_area("통화 내용 요약")
            status = st.selectbox(
                "처리 상태", CALL_STATUSES
            )

            submitted = st.form_submit_button(
                "전화 기록 저장",
                type="primary",
            )

        if submitted:
            try:
                add_call(
                    caller, phone, category, summary, status
                )
                st.success("전화 기록을 저장했습니다.")
                st.rerun()
            except (sqlite3.Error, OSError):
                st.error("전화 기록 저장에 실패했습니다.")


# -------------------------
# 매출 입력
# -------------------------
def sales_entry_form():
    with st.expander("➕ 매출 내역 추가", expanded=True):
        with st.form("sales_form", clear_on_submit=True):
            sale_date = st.date_input(
                "매출 날짜", value=date.today()
            )
            product = st.text_input(
                "상품명", placeholder="예: 음료"
            )
            quantity = st.number_input(
                "수량", min_value=1, value=1, step=1
            )
            unit_price = st.number_input(
                "개당 판매 가격(원)",
                min_value=0,
                value=0,
                step=100,
            )
            note = st.text_input("메모(선택)")

            st.caption(
                f"예상 매출: {int(quantity) * int(unit_price):,}원"
            )

            submitted = st.form_submit_button(
                "매출 저장",
                type="primary",
            )

        if submitted:
            if not product.strip():
                st.warning("상품명을 입력해 주세요.")
            else:
                try:
                    add_sale(
                        sale_date,
                        product,
                        quantity,
                        unit_price,
                        note,
                    )
                    st.success("매출 내역을 저장했습니다.")
                    st.rerun()
                except (sqlite3.Error, OSError, ValueError):
                    st.error("매출 저장에 실패했습니다.")


# -------------------------
# 대시보드
# -------------------------
@st.fragment(run_every="5s")
def dashboard():
    try:
        calls = load_calls()
        sales = load_sales()
    except (sqlite3.Error, pd.errors.DatabaseError, OSError):
        st.error("데이터를 불러오지 못했습니다.")
        return

    total_calls = len(calls)
    pending = (
        int((calls["status"] != "완료").sum())
        if not calls.empty else 0
    )
    completed = (
        int((calls["status"] == "완료").sum())
        if not calls.empty else 0
    )
    total_sales = (
        int(sales["total"].sum())
        if not sales.empty else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체 전화", f"{total_calls:,}건")
    c2.metric("미완료 전화", f"{pending:,}건")
    c3.metric("완료 전화", f"{completed:,}건")
    c4.metric("누적 매출", f"{total_sales:,}원")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("📊 전화 유형별 건수")

        if calls.empty:
            st.info("전화 기록을 추가해 주세요.")
        else:
            category_counts = (
                calls["category"]
                .value_counts()
                .rename_axis("전화 유형")
                .reset_index(name="건수")
            )
            st.bar_chart(
                category_counts,
                x="전화 유형",
                y="건수",
            )

    with right:
        st.subheader("📈 일별 매출")

        if sales.empty:
            st.info("매출 내역을 추가해 주세요.")
        else:
            sales_by_day = (
                sales.assign(
                    매출일=pd.to_datetime(sales["sale_date"])
                )
                .groupby("매출일", as_index=False)["total"]
                .sum()
                .rename(columns={"total": "매출(원)"})
                .sort_values("매출일")
            )
            st.line_chart(
                sales_by_day,
                x="매출일",
                y="매출(원)",
            )

    st.subheader("🕒 시간대별 전화량")

    if calls.empty:
        st.info("전화 기록을 추가하면 시간대별 통계가 표시됩니다.")
    else:
        calls["call_time"] = pd.to_datetime(
            calls["call_time"], errors="coerce"
        )
        hourly = (
            calls.dropna(subset=["call_time"])
            .assign(
                시간=lambda frame:
                    frame["call_time"].dt.floor("h")
            )
            .groupby("시간")
            .size()
            .reset_index(name="전화 건수")
            .sort_values("시간")
        )

        if hourly.empty:
            st.info("시간 통계를 계산할 기록이 없습니다.")
        else:
            st.line_chart(
                hourly, x="시간", y="전화 건수"
            )

    st.subheader("📋 최근 전화 기록")

    if calls.empty:
        st.info("아직 전화 기록이 없습니다.")
    else:
        recent = calls.head(10).rename(columns={
            "call_time": "전화 시간",
            "caller": "발신자",
            "phone": "전화번호",
            "category": "유형",
            "summary": "통화 내용",
            "status": "처리 상태",
        })

        st.dataframe(
            recent[[
                "전화 시간", "발신자", "전화번호",
                "유형", "통화 내용", "처리 상태"
            ]],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("🛍️ 상품별 매출")

    if sales.empty:
        st.info("매출 내역이 없습니다.")
    else:
        by_product = (
            sales.groupby("product", as_index=False)["total"]
            .sum()
            .rename(columns={
                "product": "상품명",
                "total": "매출(원)",
            })
            .sort_values("매출(원)", ascending=False)
        )

        st.bar_chart(
            by_product,
            x="상품명",
            y="매출(원)",
        )


# -------------------------
# 메뉴별 화면
# -------------------------
if page == "대시보드":
    dashboard()

elif page == "전화 기록":
    call_entry_form()
    st.subheader("📋 전화 기록 목록")

    try:
        df = load_calls()
    except (sqlite3.Error, pd.errors.DatabaseError, OSError):
        st.error("전화 기록을 불러오지 못했습니다.")
        st.stop()

    keyword = st.text_input(
        "발신자·전화번호·통화 내용 검색"
    )
    status_filter = st.selectbox(
        "처리 상태 필터",
        ["전체"] + CALL_STATUSES,
    )

    filtered = df.copy()

    if keyword:
        mask = pd.Series(
            False, index=filtered.index
        )
        for col in ["caller", "phone", "summary"]:
            mask |= filtered[col].fillna("").astype(str).str.contains(
                keyword,
                case=False,
                regex=False,
            )
        filtered = filtered[mask]

    if status_filter != "전체":
        filtered = filtered[
            filtered["status"] == status_filter
        ]

    display = filtered.rename(columns={
        "call_time": "전화 시간",
        "caller": "발신자",
        "phone": "전화번호",
        "category": "유형",
        "summary": "통화 내용",
        "status": "처리 상태",
    })

    st.dataframe(
        display[[
            "전화 시간", "발신자", "전화번호",
            "유형", "통화 내용", "처리 상태"
        ]],
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "📥 전화 기록 CSV 다운로드",
        data=display.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="전화_기록.csv",
        mime="text/csv",
    )

elif page == "매출 관리":
    sales_entry_form()
    st.subheader("💰 매출 내역 목록")

    try:
        df = load_sales()
    except (sqlite3.Error, pd.errors.DatabaseError, OSError):
        st.error("매출 내역을 불러오지 못했습니다.")
        st.stop()

    if df.empty:
        st.info("아직 매출 내역이 없습니다.")
    else:
        df["sale_date"] = pd.to_datetime(
            df["sale_date"], errors="coerce"
        )

        min_day = df["sale_date"].min().date()
        max_day = df["sale_date"].max().date()

        date_range = st.date_input(
            "조회 기간",
            value=(min_day, max_day),
        )

        filtered = df.copy()

        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            start_day, end_day = date_range
            filtered = filtered[
                (filtered["sale_date"].dt.date >= start_day)
                & (filtered["sale_date"].dt.date <= end_day)
            ]

        total_revenue = (
            int(filtered["total"].sum())
            if not filtered.empty else 0
        )
        total_units = (
            int(filtered["quantity"].sum())
            if not filtered.empty else 0
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("조회 기간 매출", f"{total_revenue:,}원")
        m2.metric("판매 수량", f"{total_units:,}개")
        m3.metric("판매 기록", f"{len(filtered):,}건")

        shown = filtered.rename(columns={
            "sale_date": "매출 날짜",
            "product": "상품명",
            "quantity": "수량",
            "unit_price": "개당 가격(원)",
            "total": "매출(원)",
            "note": "메모",
        })

        st.dataframe(
            shown[[
                "매출 날짜", "상품명", "수량",
                "개당 가격(원)", "매출(원)", "메모"
            ]],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "📥 매출 내역 CSV 다운로드",
            data=shown.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="매출_내역.csv",
            mime="text/csv",
        )


st.divider()
st.caption(
    "이 앱은 전화 수신을 자동 감지하거나 녹음하지 않습니다. "
    "전화 기록은 직접 입력합니다. "
    "배포 환경에서는 SQLite 데이터의 영구 보존이 보장되지 않습니다."
)
