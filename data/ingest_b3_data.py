"""
Animal Health Financial Data Ingestion
Fetches comprehensive financial data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
import duckdb
import os

TICKERS = {
    "OFSA3.SA": "Ourofino",
    "ZTS": "Zoetis",
    "ELAN": "Elanco",
}

def safe_get(df, row):
    """Safely extract a row from a DataFrame, return None if not found"""
    if df is None or df.empty:
        return None
    if row not in df.index:
        return None
    return df.loc[row]

def fetch_company_data(ticker: str, company_name: str) -> pd.DataFrame:
    print(f"Fetching data for {ticker} ({company_name})...")
    stock = yf.Ticker(ticker)

    try:
        income = stock.quarterly_income_stmt
        balance = stock.quarterly_balance_sheet
        cashflow = stock.quarterly_cashflow
        info = stock.info

        if income is None or income.empty:
            print(f"  No income data for {ticker}")
            return pd.DataFrame()

        # Use income statement dates as base
        dates = income.columns

        records = []
        for date in dates:
            def get_val(df, row):
                s = safe_get(df, row)
                if s is None or date not in s.index:
                    return None
                v = s[date]
                return None if pd.isna(v) else round(v / 1_000_000, 2)

            revenue          = get_val(income, "Total Revenue")
            gross_profit     = get_val(income, "Gross Profit")
            ebitda           = get_val(income, "EBITDA") or get_val(income, "Normalized EBITDA")
            operating_income = get_val(income, "Operating Income")
            net_income       = get_val(income, "Net Income")
            rd_expense       = get_val(income, "Research And Development")
            interest_expense = get_val(income, "Interest Expense")

            total_assets     = get_val(balance, "Total Assets")
            total_equity     = get_val(balance, "Stockholders Equity") or get_val(balance, "Common Stock Equity")
            total_debt       = get_val(balance, "Total Debt")
            cash             = get_val(balance, "Cash And Cash Equivalents")

            capex            = get_val(cashflow, "Capital Expenditure")

            # Derived metrics
            gross_margin     = round(gross_profit / revenue * 100, 1) if revenue and gross_profit else None
            ebitda_margin    = round(ebitda / revenue * 100, 1) if revenue and ebitda else None
            net_margin       = round(net_income / revenue * 100, 1) if revenue and net_income else None
            net_debt         = round(total_debt - cash, 2) if total_debt and cash else None
            net_debt_ebitda  = None  # calculated post-processing using LTM EBITDA
            roe              = round(net_income / total_equity * 100, 1) if net_income and total_equity and total_equity != 0 else None
            roa              = round(net_income / total_assets * 100, 1) if net_income and total_assets and total_assets != 0 else None
            rd_pct_revenue   = round(rd_expense / revenue * 100, 1) if rd_expense and revenue else None
            interest_coverage= round(operating_income / abs(interest_expense), 1) if operating_income and interest_expense and interest_expense != 0 else None
            fcf              = round((ebitda or 0) - abs(capex or 0), 2) if ebitda else None

            # Market data from info (point-in-time)
            ev_ebitda        = round(info.get("enterpriseToEbitda"), 2) if info.get("enterpriseToEbitda") else None
            pe_ratio         = round(info.get("trailingPE"), 2) if info.get("trailingPE") else None
            ps_ratio         = round(info.get("priceToSalesTrailing12Months"), 2) if info.get("priceToSalesTrailing12Months") else None
            market_cap       = round(info.get("marketCap", 0) / 1_000_000, 0) if info.get("marketCap") else None

            records.append({
                "ticker":           ticker.replace(".SA", ""),
                "company_name":     company_name,
                "date":             pd.to_datetime(date),
                "year":             pd.to_datetime(date).year,
                "quarter":          pd.to_datetime(date).quarter,
                "period":           f"Q{pd.to_datetime(date).quarter} {pd.to_datetime(date).year}",
                # Income statement
                "revenue_millions":         revenue,
                "gross_profit_millions":    gross_profit,
                "ebitda_millions":          ebitda,
                "operating_income_millions":operating_income,
                "net_income_millions":      net_income,
                "rd_expense_millions":      rd_expense,
                # Margins
                "gross_margin_pct":         gross_margin,
                "ebitda_margin_pct":        ebitda_margin,
                "net_margin_pct":           net_margin,
                "rd_pct_revenue":           rd_pct_revenue,
                # Balance sheet
                "total_assets_millions":    total_assets,
                "total_equity_millions":    total_equity,
                "total_debt_millions":      total_debt,
                "net_debt_millions":        net_debt,
                "net_debt_ebitda":          net_debt_ebitda,
                # Returns
                "roe_pct":                  roe,
                "roa_pct":                  roa,
                "interest_coverage":        interest_coverage,
                # Cash flow
                "capex_millions":           capex,
                "fcf_millions":             fcf,
                # Valuation (current)
                "ev_ebitda":                ev_ebitda,
                "pe_ratio":                 pe_ratio,
                "ps_ratio":                 ps_ratio,
                "market_cap_millions":      market_cap,
            })

        df = pd.DataFrame(records)
        print(f"  {len(df)} quarters fetched")
        return df

    except Exception as e:
        print(f"  Error: {e}")
        return pd.DataFrame()


def main():
    all_data = []

    for ticker, name in TICKERS.items():
        df = fetch_company_data(ticker, name)
        if not df.empty:
            all_data.append(df)

    if not all_data:
        print("No data fetched.")
        return

    combined = pd.concat(all_data, ignore_index=True)
    combined = combined.sort_values(["ticker", "year", "quarter"]).reset_index(drop=True)

    # Calculate Net Debt / EBITDA using LTM (last 4 quarters rolling sum)
    combined["ebitda_ltm"] = (
        combined.groupby("ticker")["ebitda_millions"]
        .transform(lambda x: x.rolling(4, min_periods=4).sum())
    )
    combined["net_debt_ebitda"] = combined.apply(
        lambda r: round(r["net_debt_millions"] / r["ebitda_ltm"], 2)
        if pd.notna(r["net_debt_millions"]) and pd.notna(r["ebitda_ltm"]) and r["ebitda_ltm"] != 0
        else None,
        axis=1
    )
    combined = combined.drop(columns=["ebitda_ltm"])

    print(f"\nTotal records: {len(combined)}")

    db_path = os.path.join(os.path.dirname(__file__), "b3_financials.duckdb")
    con = duckdb.connect(db_path)

    con.execute("DROP TABLE IF EXISTS financials")
    con.execute("CREATE TABLE financials AS SELECT * FROM combined")

    print(f"Saved to {db_path} — table 'financials' with {len(combined)} rows")
    con.close()


if __name__ == "__main__":
    main()
