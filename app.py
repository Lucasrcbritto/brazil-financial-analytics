"""
Brazil Financial Analytics Dashboard
Interactive dashboard for B3 listed companies financial KPIs
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Page config
st.set_page_config(
    page_title="Brazil Financial Analytics",
    page_icon="📊",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    db_path = os.path.join(os.path.dirname(__file__), "data", "b3_financials.duckdb")
    con = duckdb.connect(db_path, read_only=True)

    df = con.execute("""
        SELECT
            ticker,
            year,
            quarter,
            revenue_millions,
            -- QoQ growth
            LAG(revenue_millions) OVER (
                PARTITION BY ticker ORDER BY year, quarter
            ) AS prev_quarter_revenue,
            ROUND(
                (revenue_millions - LAG(revenue_millions) OVER (
                    PARTITION BY ticker ORDER BY year, quarter
                )) / LAG(revenue_millions) OVER (
                    PARTITION BY ticker ORDER BY year, quarter
                ) * 100, 1
            ) AS qoq_growth_pct,
            -- YTD
            ROUND(SUM(revenue_millions) OVER (
                PARTITION BY ticker, year
                ORDER BY quarter
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ), 1) AS revenue_ytd,
            -- Period label
            CONCAT('Q', quarter, ' ', year) AS period
        FROM raw_revenue
        ORDER BY ticker, year, quarter
    """).df()

    con.close()
    return df


# Header
st.title("📊 Brazil Financial Analytics")
st.markdown("Automated financial analytics pipeline — B3 listed companies")
st.divider()

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_tickers = st.sidebar.multiselect(
    "Select companies",
    options=sorted(df["ticker"].unique()),
    default=sorted(df["ticker"].unique())
)

selected_years = st.sidebar.multiselect(
    "Select years",
    options=sorted(df["year"].unique()),
    default=sorted(df["year"].unique())
)

# Filter data
filtered = df[
    (df["ticker"].isin(selected_tickers)) &
    (df["year"].isin(selected_years))
]

# KPI Cards
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    total_revenue = filtered["revenue_millions"].sum()
    st.metric("Total Revenue (filtered)", f"R$ {total_revenue:,.0f}M")

with col2:
    avg_qoq = filtered["qoq_growth_pct"].mean()
    st.metric("Avg QoQ Growth", f"{avg_qoq:.1f}%" if pd.notna(avg_qoq) else "N/A")

with col3:
    companies = filtered["ticker"].nunique()
    st.metric("Companies", companies)

st.divider()

# Revenue over time
st.subheader("Quarterly Revenue by Company")
fig_revenue = px.line(
    filtered,
    x="period",
    y="revenue_millions",
    color="ticker",
    markers=True,
    labels={"revenue_millions": "Revenue (R$ millions)", "period": "Period", "ticker": "Company"},
    template="plotly_dark"
)
fig_revenue.update_layout(height=400)
st.plotly_chart(fig_revenue, use_container_width=True)

# QoQ Growth
st.subheader("Quarter-over-Quarter Revenue Growth (%)")
qoq_data = filtered.dropna(subset=["qoq_growth_pct"])
fig_qoq = px.bar(
    qoq_data,
    x="period",
    y="qoq_growth_pct",
    color="ticker",
    barmode="group",
    labels={"qoq_growth_pct": "QoQ Growth (%)", "period": "Period", "ticker": "Company"},
    template="plotly_dark"
)
fig_qoq.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
fig_qoq.update_layout(height=400)
st.plotly_chart(fig_qoq, use_container_width=True)

# Raw data table
st.subheader("Raw Data")
st.dataframe(
    filtered[["ticker", "year", "quarter", "revenue_millions", "qoq_growth_pct", "revenue_ytd"]],
    use_container_width=True,
    hide_index=True
)

st.divider()
st.caption("Data source: Yahoo Finance via yfinance | Pipeline: Python + dbt + DuckDB | Built by Lucas Britto")
