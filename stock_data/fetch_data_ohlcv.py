import os
import re
import time
import datetime as dt
import pandas as pd
import yfinance as yf

# =======================
# CONFIG
# =======================
INPUT_FILE = "sorted_stocks_by_marketcap.csv"

START_DATE = "2021-01-14"   # 14 Jan 2021
END_DATE = (dt.date.today() + dt.timedelta(days=1)).strftime("%Y-%m-%d")

START_SERIAL = 200
END_SERIAL = 400            # ✅ inclusive → 201 stocks

OUT_DIR = "yahoo_ohlcv_200_to_400"
SLEEP_SECONDS = 0.8         # increase if rate-limited

TRY_SUFFIXES = [".NS", ".BO"]  # Yahoo Finance India suffixes
# =======================


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w.\-]+", "_", name.strip())


def find_symbol_column(df: pd.DataFrame) -> str:
    for c in df.columns:
        if c.strip().lower() == "symbol":
            return c
    raise ValueError("❌ No 'Symbol' column found in CSV")


def download_from_yahoo(symbol: str):
    symbol = symbol.strip()

    # If suffix already exists, try directly
    candidates = [symbol] if "." in symbol else [symbol + s for s in TRY_SUFFIXES]

    for ticker in candidates:
        try:
            df = yf.download(
                ticker,
                start=START_DATE,
                end=END_DATE,
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=False
            )
            if not df.empty:
                return ticker, df
        except Exception:
            pass

    return "", pd.DataFrame()


def main():
    df = pd.read_csv(INPUT_FILE)
    symbol_col = find_symbol_column(df)

    # ✅ serial 200–400 inclusive → iloc[199:400]
    stocks = df.iloc[START_SERIAL - 1 : END_SERIAL][symbol_col].astype(str).tolist()

    os.makedirs(OUT_DIR, exist_ok=True)

    success, failed = 0, []

    print(f"\nDownloading {len(stocks)} stocks (Serial {START_SERIAL}–{END_SERIAL})")
    print(f"Date range: {START_DATE} → today")
    print(f"Saving to folder: {OUT_DIR}\n")

    for i, sym in enumerate(stocks, start=START_SERIAL):
        clean_name = sanitize_filename(sym)
        out_file = os.path.join(OUT_DIR, f"{clean_name}.csv")

        ticker_used, data = download_from_yahoo(sym)

        if data.empty:
            print(f"[{i}] ❌ FAILED : {sym}")
            failed.append(sym)
        else:
            data = data.reset_index()
            data = data[["Date", "Open", "High", "Low", "Close", "Volume"]]
            data.to_csv(out_file, index=False)

            print(f"[{i}] ✅ SAVED  : {out_file}  ({ticker_used})")
            success += 1

        time.sleep(SLEEP_SECONDS)

    print("\n===== SUMMARY =====")
    print(f"CSV files saved : {success}")
    print(f"Failed symbols  : {len(failed)}")

    if failed:
        with open(os.path.join(OUT_DIR, "failed_symbols.txt"), "w") as f:
            for s in failed:
                f.write(s + "\n")
        print("Failed symbols written to failed_symbols.txt")


if __name__ == "__main__":
    main()
