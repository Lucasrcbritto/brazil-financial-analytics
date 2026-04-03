# Brazil Financial Analytics

**Automated financial analytics pipeline for B3 listed companies — built with Python, dbt, SQL, and Streamlit.**

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-Streamlit-red)](https://brazil-financial-analytics-r99t4ozuok8znvjljcwpyn.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://python.org)
[![dbt](https://img.shields.io/badge/dbt-1.11-orange)](https://getdbt.com)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.5-yellow)](https://duckdb.org)

---

## Live Demo

**[→ Open Dashboard](https://brazil-financial-analytics-r99t4ozuok8znvjljcwpyn.streamlit.app)**

---

## Overview

This project builds an end-to-end financial analytics pipeline that:

1. **Ingests** live quarterly financial data from B3 listed companies via `yfinance`
2. **Transforms** raw data through a dbt pipeline (staging → intermediate → marts)
3. **Calculates** financial KPIs: quarterly revenue, QoQ growth, YTD cumulative revenue
4. **Delivers** an interactive Streamlit dashboard with filters and visualizations

---

## Companies Analyzed

| Ticker | Company |
|--------|---------|
| IGTI3 | Iguatemi |
| WEGE3 | WEG |
| RENT3 | Localiza |
| RDOR3 | Rede D'Or |
| MELI34 | MercadoLibre BDR |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Data Ingestion | Python + yfinance |
| Storage | DuckDB |
| Transformation | dbt Core + DuckDB adapter |
| Dashboard | Streamlit + Plotly |
| Version Control | Git + GitHub |

---

## dbt Architecture

```
seeds/
└── receita_bruta.csv          # Raw revenue data

models/
├── staging/
│   └── stg_receita.sql        # Standardize and rename columns
├── intermediate/
│   └── int_receita_crescimento.sql  # Calculate QoQ growth and YTD
└── marts/
    └── fct_kpis_financeiros.sql     # Final analytical table with all KPIs
```

---

## Key Metrics

- **QoQ Growth (%)** — Quarter-over-quarter revenue growth per company
- **YTD Revenue** — Year-to-date cumulative revenue
- **YoY Growth (%)** — Year-over-year annual revenue growth

---

## How to Run Locally

```bash
# Clone the repository
git clone https://github.com/Lucasrcbritto/brazil-financial-analytics.git
cd brazil-financial-analytics

# Install dependencies
pip install -r requirements.txt

# Fetch fresh data from Yahoo Finance
python data/ingest_b3_data.py

# Run dbt pipeline
cd financeiro
dbt seed
dbt run
dbt test

# Launch dashboard
cd ..
streamlit run app.py
```

---

## Project Structure

```
brazil-financial-analytics/
├── app.py                    # Streamlit dashboard
├── requirements.txt          # Python dependencies
├── data/
│   ├── ingest_b3_data.py     # Data ingestion script
│   └── b3_financials.duckdb  # Local DuckDB database
├── financeiro/               # dbt project
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── seeds/
└── notebooks/                # Exploratory analysis
```

---

## Author

**Lucas Rodrigues da Cunha de Britto**
- Economist | FP&A & Investor Relations | B3 listed companies (Iguatemi S.A., Ourofino S.A.)
- BSc in Econometrics — University of South Florida
- [GitHub](https://github.com/Lucasrcbritto)
