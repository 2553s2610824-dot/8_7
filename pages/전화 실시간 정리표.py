
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(
    page_title="전화 및 매출 관리",
    page_icon="📞",
    layout="wide"
)

DB_PATH = "business_data.db"

# ---------------------------
# 데이터베이스 생성
# ---------------------------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_time TEXT,
                caller TEXT,
                phone TEXT,
                category TEXT,
                summary TEXT,
                status TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_time TEXT,
                product TEXT,
                quantity INTEGER,
                unit_price INTEGER,
                total INTEGER,
                payment TEXT
            )
        """)

init_db()

# ---------------------------
# 전화 기록 함수
# ---------------------------
def add_call(caller, phone, category, summary, status):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO calls
            (call_time, caller, phone, category, summary, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            caller, phone, category, summary, status
        ))

def load_calls():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            "SELECT * FROM calls ORDER BY id DESC", conn
        )

# ---------------------------
# 매출 기록 함수
# ---------------------------
def add_sale(product, quantity, unit_price, payment):
    total = quantity * unit_price

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO sales
            (sale_time, product, quantity, unit_price, total, payment)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            product, quantity, unit_price, total, payment
        ))

def load_sales():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            "SELECT * FROM sales ORDER BY id DESC", conn
        )

# ---------------------------
# 화면 제목
# ---------------------------
st.title("📞 전화 실시간 정리표 & 매출 관리")
st.caption("전화 기록과 매출을 한곳에서 관리하세요.")

# ---------------------------
# 메뉴
# ---------------------------
menu = st.sidebar.radio(
    "메뉴 선택",
    ["대시보드", "전화 기록", "매출 기록"]
)

# ===========================
# 대시보드
# ===========================
if menu == "대시보드":
    st.header("📊 전체 현황")

    calls = load_calls()
    sales = load_sales()

    total_calls = len(calls)
    total_sales = int(sales["total"].sum()) if not sales.empty else 0
    total_orders = len(sales)

    col1, col2, col3 = st.columns(3)

    col1.metric("전체 전화 기록", f"{total_calls}건")
    col2.metric("전체 매출", f"{total_sales:,}원")
    col3.metric("판매 기록", f"{total_orders}건")

    st.divider()

    # 일별 매출 그래프
    st.subheader("📈 일별 매출")

    if not sales.empty:
        sales["sale_time"] = pd.to_datetime(sales["sale_time"])
        sales["날짜"] = sales["sale_time"].dt.strftime("%Y-%m-%d")

        daily_sales = (
            sales.groupby("날짜", as_index=False)["total"]
            .sum()
            .rename(columns={"total": "매출"})
            .sort_values("날짜")
        )

        st.line_chart(
            daily_sales,
            x="날짜",
            y="매출"
        )
    else:
        st.info("매출 기록을 추가하면 그래프가 표시됩니다.")

    # 상품별 매출 그래프
    st.subheader("📦 상품별 매출")

    if not sales.empty:
        product_sales = (
            sales.groupby("product", as_index=False)["total"]
            .sum()
            .rename(columns={
                "product": "상품명",
                "total": "매출"
            })
            .sort_values("매출", ascending=False)
        )

        st.bar_chart(
            product_sales,
            x="상품명",
            y="매출"
        )

    # 최근 전화 기록
    st.subheader("☎️ 최근 전화 기록")

    if not calls.empty:
        st.dataframe(
            calls.head(10),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("아직 전화 기록이 없습니다.")

    # 최근 매출 기록
    st.subheader("💰 최근 매출 기록")

    if not sales.empty:
        st.dataframe(
            sales.head(10),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("아직 매출 기록이 없습니다.")

# ===========================
# 전화 기록 페이지
# ===========================
elif menu == "전화 기록":
    st.header("☎️ 전화 기록 관리")

    with st.form("call_form"):
        caller = st.text_input("발신자 이름")
        phone = st.text_input("전화번호")

        category = st.selectbox(
            "전화 유형",
            ["문의", "예약", "주문", "불만", "업무", "기타"]
        )

        summary = st.text_area("통화 내용 요약")

        status = st.selectbox(
            "처리 상태",
            ["미처리", "처리 중", "완료"]
        )

        submitted = st.form_submit_button("전화 기록 저장")

        if submitted:
            add_call(caller, phone, category, summary, status)
            st.success("전화 기록을 저장했습니다.")
            st.rerun()

    calls = load_calls()

    st.subheader("📋 저장된 전화 기록")

    if not calls.empty:
        st.dataframe(calls, use_container_width=True, hide_index=True)

        st.download_button(
            "전화 기록 CSV 다운로드",
            data=calls.to_csv(index=False).encode("utf-8-sig"),
            file_name="전화기록.csv",
            mime="text/csv"
        )
    else:
        st.info("전화 기록이 없습니다.")

# ===========================
# 매출 기록 페이지
# ===========================
elif menu == "매출 기록":
    st.header("💰 매출 기록 관리")

    with st.form("sales_form"):
        product = st.text_input("상품명")

        quantity = st.number_input(
            "판매 수량",
            min_value=1,
            value=1,
            step=1
        )

        unit_price = st.number_input(
            "상품 단가 (원)",
            min_value=0,
            value=10000,
            step=1000
        )

        payment = st.selectbox(
            "결제 방법",
            ["카드", "현금", "계좌이체", "기타"]
        )

        st.write(
            f"예상 매출: **{quantity * unit_price:,}원**"
        )

        submitted = st.form_submit_button("매출 저장")

        if submitted:
            if not product.strip():
                st.error("상품명을 입력해 주세요.")
            else:
                add_sale(
                    product.strip(),
                    int(quantity),
                    int(unit_price),
                    payment
                )
                st.success("매출 기록을 저장했습니다.")
                st.rerun()

    sales = load_sales()

    st.divider()
    st.subheader("📊 매출 요약")

    if not sales.empty:
        total_sales = int(sales["total"].sum())
        total_quantity = int(sales["quantity"].sum())

        c1, c2 = st.columns(2)
        c1.metric("누적 매출", f"{total_sales:,}원")
        c2.metric("총 판매 수량", f"{total_quantity:,}개")

        st.subheader("🧾 매출 상세 기록")

        st.dataframe(
            sales,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "매출 기록 CSV 다운로드",
            data=sales.to_csv(index=False).encode("utf-8-sig"),
            file_name="매출기록.csv",
            mime="text/csv"
        )
    else:
        st.info("아직 매출 기록이 없습니다.")
