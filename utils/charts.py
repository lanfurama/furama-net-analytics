import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .load import TX_GROUP_LABELS


def _fmt_vnd(x):
    if abs(x) >= 1e9:
        return f"{x / 1e9:.1f}B"
    if abs(x) >= 1e6:
        return f"{x / 1e6:.1f}M"
    if abs(x) >= 1e3:
        return f"{x / 1e3:.1f}K"
    return str(int(x))


def line_daily_net(df: pd.DataFrame) -> go.Figure:
    daily = df.groupby([df["Transaction Date"].dt.date, "period"])["Net Amount"].sum().reset_index()
    daily["Transaction Date"] = pd.to_datetime(daily["Transaction Date"])
    fig = px.line(
        daily,
        x="Transaction Date",
        y="Net Amount",
        color="period",
        title="Daily net revenue (Jan 2025 vs Jan 2026)",
    )
    fig.update_layout(yaxis_tickformat=",", legend_title="January")
    fig.update_yaxes(title_text="Net Amount (VND)")
    return fig


def bar_country_net(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    by_country = (
        df.groupby(["Country", "period"])["Net Amount"]
        .sum()
        .reset_index()
    )
    top_countries = (
        df.groupby("Country")["Net Amount"]
        .sum()
        .nlargest(top_n)
        .index.tolist()
    )
    by_country = by_country[by_country["Country"].isin(top_countries)]
    fig = px.bar(
        by_country,
        x="Country",
        y="Net Amount",
        color="period",
        barmode="group",
        title=f"Net by country (Top {top_n}) – Jan 2025 vs Jan 2026",
    )
    fig.update_layout(yaxis_tickformat=",", xaxis_tickangle=-45)
    fig.update_yaxes(title_text="Net Amount (VND)")
    return fig


def bar_tx_group(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["Group Label"] = df["Transaction Code Group"].map(
        lambda x: TX_GROUP_LABELS.get(x, str(x))
    )
    by_group = (
        df.groupby(["Group Label", "period"])["Net Amount"]
        .sum()
        .reset_index()
    )
    fig = px.bar(
        by_group,
        x="Group Label",
        y="Net Amount",
        color="period",
        barmode="group",
        title="Net by transaction group – Jan 2025 vs Jan 2026",
    )
    fig.update_layout(yaxis_tickformat=",", xaxis_tickangle=-30)
    fig.update_yaxes(title_text="Net Amount (VND)")
    return fig


def stacked_bar_revenue_mix(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["Group Label"] = df["Transaction Code Group"].map(
        lambda x: TX_GROUP_LABELS.get(x, str(x))
    )
    exclude = ["VAT", "Service"]
    by_group = (
        df[~df["Group Label"].isin(exclude)]
        .groupby(["Group Label", "period"])["Net Amount"]
        .sum()
        .reset_index()
    )
    fig = px.bar(
        by_group,
        x="period",
        y="Net Amount",
        color="Group Label",
        barmode="stack",
        title="Revenue mix (excl. VAT, Service) – Jan 2025 vs Jan 2026",
    )
    fig.update_layout(yaxis_tickformat=",", xaxis_title="January")
    fig.update_yaxes(title_text="Net Amount (VND)")
    return fig


ROOM_TYPE_EXCLUDE = {"PF", "PM"}


def bar_room_type(df: pd.DataFrame, top_n: int = 12) -> go.Figure:
    room_col = "Room Type" if "Room Type" in df.columns else "Room Class"
    df = df[(df[room_col].str.strip() != "") & (~df[room_col].str.strip().isin(ROOM_TYPE_EXCLUDE))]
    by_room = (
        df.groupby([room_col, "period"])["Net Amount"]
        .sum()
        .reset_index()
    )
    top_rooms = (
        df.groupby(room_col)["Net Amount"]
        .sum()
        .nlargest(top_n)
        .index.tolist()
    )
    by_room = by_room[by_room[room_col].isin(top_rooms)]
    fig = px.bar(
        by_room,
        x=room_col,
        y="Net Amount",
        color="period",
        barmode="group",
        title=f"Net by room type – Jan 2025 vs Jan 2026",
    )
    fig.update_layout(yaxis_tickformat=",", xaxis_tickangle=-45)
    fig.update_yaxes(title_text="Net Amount (VND)")
    return fig


def pie_tx_group_period(df: pd.DataFrame, period: int) -> go.Figure:
    df = df[df["period"] == period].copy()
    df["Group Label"] = df["Transaction Code Group"].map(
        lambda x: TX_GROUP_LABELS.get(x, str(x))
    )
    by_group = df.groupby("Group Label")["Net Amount"].sum().reset_index()
    fig = px.pie(
        by_group,
        values="Net Amount",
        names="Group Label",
        title=f"Net mix by transaction group – Jan {period}",
    )
    return fig


def treemap_net_by_period_group(df: pd.DataFrame) -> go.Figure:
    agg = (
        df.groupby(["period", "Transaction Code Group"])["Net Amount"]
        .sum()
        .reset_index()
    )
    agg["Group Label"] = agg["Transaction Code Group"].map(
        lambda x: TX_GROUP_LABELS.get(x, str(x))
    )
    agg["period"] = agg["period"].astype(str)
    fig = px.treemap(
        agg,
        path=["period", "Group Label"],
        values="Net Amount",
        title="Net revenue by year and category (Jan 2025 vs Jan 2026)",
    )
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    return fig


def bar_top_descriptions(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    by_desc = (
        df.groupby(["Transaction Code Description", "period"])["Net Amount"]
        .sum()
        .reset_index()
    )
    top_desc = (
        df.groupby("Transaction Code Description")["Net Amount"]
        .sum()
        .nlargest(top_n)
        .index.tolist()
    )
    by_desc = by_desc[by_desc["Transaction Code Description"].isin(top_desc)]
    fig = px.bar(
        by_desc,
        x="Transaction Code Description",
        y="Net Amount",
        color="period",
        barmode="group",
        title=f"Top {top_n} transaction descriptions by Net – Jan 2025 vs Jan 2026",
    )
    fig.update_layout(yaxis_tickformat=",", xaxis_tickangle=-45)
    fig.update_yaxes(title_text="Net Amount (VND)")
    return fig
