"""
B3 Financial Data Ingestion
Fetches quarterly financial data from Yahoo Finance for selected B3 companies
"""

import yfinance as yf
import pandas as pd
import duckdb
import os

# B3 companies to analyze
TICKERS = [
    "IGTI3.SA",   # Iguatemi
    "WEGE3.SA",   # WEG
    "RENT3.SA",   # Localiza
    "RDOR3.SA",   # Rede D'Or
    "MELI34.SA",   # MercadoLibre BDR
    "OFSA3.SA",   # Ourofino S.A
]

def fetch_financials(ticker: str) -> pd.DataFrame:
    """Fetch quarterly income statement data from Yahoo Finance"""
    print(f"Fetching data for {ticker}...")

    stock = yf.Ticker(ticker)

    try:
        # Get quarterly financials
        financials = stock.quarterly_income_stmt

        if financials is None or financials.empty:
            print(f"  No data available for {ticker}")
            return pd.DataFrame()

        # Extract revenue row
        if "Total Revenue" not in financials.index:
            print(f"  No revenue data for {ticker}")
            return pd.DataFrame()

        revenue = financials.loc["Total Revenue"].dropna()

        records = []
        for date, value in revenue.items():
            records.append({
                "ticker": ticker.replace(".SA", ""),
                "date": pd.to_datetime(date),
                "year": pd.to_datetime(date).year,
                "quarter": pd.to_datetime(date).quarter,
                "revenue_millions": round(value / 1_000_000, 2)
            })

        df = pd.DataFrame(records)
        print(f"  Found {len(df)} quarters of data")
        return df

    except Exception as e:
        print(f"  Error fetching {ticker}: {e}")
        return pd.DataFrame()


def main():
    all_data = []

    for ticker in TICKERS:
        df = fetch_financials(ticker)
        if not df.empty:
            all_data.append(df)

    if not all_data:
        print("No data fetched. Exiting.")
        return

    # Combine all companies
    combined = pd.concat(all_data, ignore_index=True)
    combined = combined.sort_values(["ticker", "year", "quarter"])

    print(f"\nTotal records fetched: {len(combined)}")
    print(combined.head(10))

    # Save to DuckDB
    db_path = os.path.join(os.path.dirname(__file__), "b3_financials.duckdb")
    con = duckdb.connect(db_path)

    con.execute("DROP TABLE IF EXISTS raw_revenue")
    con.execute("""
        CREATE TABLE raw_revenue AS
        SELECT * FROM combined
    """)

    print(f"\nData saved to {db_path}")
    print(f"Table 'raw_revenue' created with {len(combined)} rows")

    con.close()


if __name__ == "__main__":
    main()
