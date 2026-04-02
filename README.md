# brazil-financial-analytics

Automated financial analytics pipeline built with Python, dbt, and SQL.

## Overview
This project ingests financial data from 15+ Brazilian listed companies (B3),
transforms it using dbt, and delivers KPIs and valuation metrics via an
interactive Streamlit dashboard.

## Stack
- Python (yfinance, pandas, duckdb, streamlit, plotly)
- dbt Core + DuckDB
- Git/GitHub

## Status
🚧 Work in progress

## How to Run Locally

```bash
# Clone the repository
git clone https://github.com/Lucasrcbritto/brazil-financial-analytics.git
cd brazil-financial-analytics

# Install dependencies
pip install -r requirements.txt
