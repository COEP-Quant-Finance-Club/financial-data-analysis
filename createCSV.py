import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

nifty_df = pd.read_csv("ind_nifty200list.csv")

tickers = (nifty_df["Symbol"].astype(str) + ".NS").tolist()

end_date = datetime.now()
start_date = end_date - timedelta(days=5 * 365)

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

BATCH_SIZE = 20
ticker_batches = list(chunk_list(tickers, BATCH_SIZE))

all_stocks_df = pd.DataFrame()

for batch in ticker_batches:
    try:
        print(f"Processing batch: {batch}")

        df = yf.download(
            batch,
            start=start_date,
            end=end_date,
            progress=False,
            group_by="ticker",
            threads=True
        )

        if df.empty:
            print(f"Failed to download data for batch {batch}, skipping...")
            continue

        # Target columns: Open, High, Low, Close
        target_cols = ['Open', 'High', 'Low', 'Close']

        if isinstance(df.columns, pd.MultiIndex):
            # Use IndexSlice to select all tickers in the batch and specific OHLC columns
            idx = pd.IndexSlice
            
            available_cols = [c for c in target_cols if c in df.columns.get_level_values(1)]
            if not available_cols:
                print(f"No OHLC data found for batch {batch}")
                continue
            
            # Select columns
            ohlc_df = df.loc[:, idx[:, available_cols]]
        else:
            # Single ticker returned, wrap in MultiIndex
            available_cols = [c for c in target_cols if c in df.columns]
            if not available_cols:
                 print(f"No OHLC data found for batch {batch}")
                 continue
            
            ohlc_df = df[available_cols]
            
            ticker_name = batch[0]
            ohlc_df.columns = pd.MultiIndex.from_product([[ticker_name], ohlc_df.columns])

        ohlc_df.index = pd.to_datetime(ohlc_df.index)

        if all_stocks_df.empty:
            all_stocks_df = ohlc_df
        else:
            all_stocks_df = pd.concat([all_stocks_df, ohlc_df], axis=1)

        time.sleep(0.2)

    except Exception as exception:
        print(f"Error in batch {batch}: {exception}")

all_stocks_df.to_csv("nifty200.csv")
print("Done")