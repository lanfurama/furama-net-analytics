import streamlit as st
import pandas as pd
from pathlib import Path

from utils.load import load_data, TX_GROUP_LABELS
from utils import charts

st.set_page_config(page_title="Furama Resort Đà Nẵng – So sánh 1/2026 vs 1/2025", layout="wide")

base_path = Path(__file__).resolve().parent
df_raw = load_data(base_path)
df = df_raw.dropna(subset=["Transaction Date"])

# Sidebar
st.sidebar.header("Lọc")
top_n = st.sidebar.slider("Top N (quốc gia / phòng / mô tả)", 5, 30, 15)
countries = sorted(df["Country"].unique().tolist())
filter_country = st.sidebar.multiselect("Quốc gia (để trống = tất cả)", countries)
if filter_country:
    df = df[df["Country"].isin(filter_country)]

df_2025 = df[df["period"] == 2025]
df_2026 = df[df["period"] == 2026]

# KPIs
net_2025 = df_2025["Net Amount"].sum()
net_2026 = df_2026["Net Amount"].sum()
pct_net = ((net_2026 - net_2025) / net_2025 * 100) if net_2025 else 0
tx_2025 = len(df_2025)
tx_2026 = len(df_2026)
pct_tx = ((tx_2026 - tx_2025) / tx_2025 * 100) if tx_2025 else 0
guests_2025 = df_2025["First Name"].dropna().astype(str).str.strip()
guests_2025 = guests_2025[guests_2025 != ""].nunique()
guests_2026 = df_2026["First Name"].dropna().astype(str).str.strip()
guests_2026 = guests_2026[guests_2026 != ""].nunique()
pct_guests = ((guests_2026 - guests_2025) / guests_2025 * 100) if guests_2025 else 0

st.title("Furama Resort Đà Nẵng – So sánh tháng 1/2026 vs 1/2025")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Tổng quan",
    "Theo quốc gia",
    "Theo nhóm giao dịch",
    "Theo loại phòng",
    "Chi tiết",
])

with tab1:
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Net 1/2025 (VND)", f"{net_2025:,.0f}", "")
    with c2:
        st.metric("Net 1/2026 (VND)", f"{net_2026:,.0f}", f"{pct_net:+.1f}%")
    with c3:
        st.metric("Số giao dịch 1/2025", f"{tx_2025:,}", "")
    with c4:
        st.metric("Số giao dịch 1/2026", f"{tx_2026:,}", f"{pct_tx:+.1f}%")
    with c5:
        st.metric("Khách (unique) 1/2025 vs 1/2026", f"{guests_2025:,} → {guests_2026:,}", f"{pct_guests:+.1f}%")
    st.plotly_chart(charts.line_daily_net(df), use_container_width=True)

with tab2:
    st.plotly_chart(charts.bar_country_net(df, top_n=top_n), use_container_width=True)
    by_country = df.groupby(["Country", "period"])["Net Amount"].sum().unstack(fill_value=0)
    by_country["Change %"] = (
        (by_country[2026] - by_country[2025]) / by_country[2025].replace(0, pd.NA) * 100
    )
    by_country = by_country.sort_values(2026, ascending=False).head(top_n * 2)
    by_country.columns = ["Net 1/2025", "Net 1/2026", "Change %"]
    st.dataframe(by_country.style.format({"Net 1/2025": "{:,.0f}", "Net 1/2026": "{:,.0f}", "Change %": "{:+.1f}%"}), use_container_width=True)

with tab3:
    st.plotly_chart(charts.bar_tx_group(df), use_container_width=True)
    st.plotly_chart(charts.stacked_bar_revenue_mix(df), use_container_width=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(charts.pie_tx_group_period(df, 2025), use_container_width=True)
    with col_b:
        st.plotly_chart(charts.pie_tx_group_period(df, 2026), use_container_width=True)

with tab4:
    st.plotly_chart(charts.bar_room_type(df, top_n=top_n), use_container_width=True)
    room_col = "Room Type"
    if room_col in df.columns:
        by_room = df.groupby([room_col, "period"])["Net Amount"].sum().unstack(fill_value=0)
        by_room["Change %"] = (by_room[2026] - by_room[2025]) / by_room[2025].replace(0, pd.NA) * 100
        by_room = by_room.sort_values(2026, ascending=False).head(top_n)
        by_room.columns = ["Net 1/2025", "Net 1/2026", "Change %"]
        st.dataframe(by_room.style.format({"Net 1/2025": "{:,.0f}", "Net 1/2026": "{:,.0f}", "Change %": "{:+.1f}%"}), use_container_width=True)

with tab5:
    st.plotly_chart(charts.bar_top_descriptions(df, top_n=top_n), use_container_width=True)
    # Top guests by Net (First Name + Country)
    df["Guest"] = df["First Name"].fillna("").astype(str) + " (" + df["Country"] + ")"
    by_guest = df.groupby(["Guest", "period"])["Net Amount"].sum().unstack(fill_value=0)
    rename_map = {c: f"Net 1/{c}" for c in by_guest.columns}
    by_guest = by_guest.rename(columns=rename_map)
    sort_col = by_guest.columns[-1]
    by_guest = by_guest.sort_values(sort_col, ascending=False).head(top_n)
    st.subheader("Top khách theo Net (First Name + Country)")
    st.dataframe(by_guest.style.format("{:,.0f}"), use_container_width=True)
    csv_export = by_guest.to_csv().encode("utf-8-sig")
    st.download_button("Tải bảng top khách (CSV)", csv_export, "top_guests.csv", "text/csv")
