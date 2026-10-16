
import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from pathlib import Path

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(
    page_title="전화 실시간 정리표",
    page_icon="☎️",
    layout="wide"
)

DB_PATH = "calls.db"

st.title("☎️ 전화 실시간 정리표")
st.caption("전화 기록을 저장하고 통계 그래프를 확인하는 관리 시스템")

# -------------------------
# 데이터베이스
# -------------------------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_time TEXT NOT NULL,
                caller TEXT,
                phone TEXT,
                category TEXT,
                summary TEXT,
                status TEXT
            )
        """)

def add_call(caller, phone, category, summary, status):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO calls
            (call_time, caller, phone, category, summary, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (now, caller, phone, category, summary, status))

def load_calls():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            "SELECT * FROM calls ORDER BY id DESC", conn
        )

init_db()

# -------------------------
# 전화 기록 입력
# -------------------------
with st.expander("➕ 새 전화 기록 추가", expanded=True):
    with st.form("call_form"):
        caller = st.text_input("발신자 이름")
        phone = st.text_input("전화번호")
        category = st.selectbox(
            "전화 유형",
            ["문의", "예약", "주문", "불만", "업무", "기타"]
        )
        summary = st.text_area("통화 내용 요약")
        status = st.selectbox(
            "처리 상태", ["미처리", "처리 중", "완료"]
        )

        submitted = st.form_submit_button("전화 기록 저장")

        if submitted:
            add_call(caller, phone, category, summary, status)
            st.success("전화 기록을 저장했습니다.")
            st.rerun()

# -------------------------
# 대시보드 자동 갱신
# -------------------------
@st.fragment(run_every="5s")
def dashboard():
    df = load_calls()

    if df.empty:
        st.info("아직 전화 기록이 없습니다. 위에서 첫 기록을 추가해 보세요.")
        return

    df["call_time"] = pd.to_datetime(df["call_time"])

    # 주요 통계
    total = len(df)
    pending = int((df["status"] != "완료").sum())
    completed = int((df["status"] == "완료").sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("전체 전화", f"{total}건")
    c2.metric("미완료 기록", f"{pending}건")
    c3.metric("완료 기록", f"{completed}건")

    st.divider()

    # 전화 유형별 그래프
    st.subheader("📊 전화 유형별 건수")
    category_counts = (
        df["category"]
        .value_counts()
        .rename_axis("전화 유형")
        .reset_index(name="건수")
    )
    st.bar_chart(category_counts, x="전화 유형", y="건수")

    # 시간대별 그래프
    st.subheader("📈 시간대별 전화량")
    hourly = (
        df.assign(시간=df["call_time"].dt.floor("h"))
        .groupby("시간")
        .size()
        .reset_index(name="전화 건수")
        .sort_values("시간")
    )
    st.line_chart(hourly, x="시간", y="전화 건수")

    # 검색
    st.subheader("📋 전화 기록표")
    keyword = st.text_input(
        "발신자·전화번호·내용 검색",
        key="search_keyword"
    )

    filtered = df.copy()
    if keyword:
        mask = (
            filtered["caller"].fillna("").str.contains(
                keyword, case=False
            )
            | filtered["phone"].fillna("").str.contains(
                keyword, case=False
            )
            | filtered["summary"].fillna("").str.contains(
                keyword, case=False
            )
        )
        filtered = filtered[mask]

    display = filtered.rename(columns={
        "call_time": "전화 시간",
        "caller": "발신자",
        "phone": "전화번호",
        "category": "유형",
        "summary": "통화 내용",
        "status": "처리 상태"
    })

    st.dataframe(
        display[[
            "전화 시간", "발신자", "전화번호",
            "유형", "통화 내용", "처리 상태"
        ]],
        use_container_width=True,
        hide_index=True
    )

    # CSV 다운로드
    csv_data = display.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 전화 기록 CSV 다운로드",
        data=csv_data,
        file_name="전화_실시간_정리표.csv",
        mime="text/csv"
    )

dashboard()
