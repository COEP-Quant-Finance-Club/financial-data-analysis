import os
import pandas as pd
import numpy as np

# ==========================================
# 1. PATHS
# ==========================================
returns_file = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\master_returns_refined_v2.csv"
market_file = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\analysis_00\daily_market_state.csv"
output_folder = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\analysis_01"

os.makedirs(output_folder, exist_ok=True)

daily_output_file = os.path.join(output_folder, "stock_market_coupling_daily.csv")
summary_output_file = os.path.join(output_folder, "stock_market_coupling_summary.csv")

# ==========================================
# 2. LOAD FILES
# ==========================================
returns_df = pd.read_csv(returns_file)
market_df = pd.read_csv(market_file)

returns_df.columns = [col.strip() for col in returns_df.columns]
market_df.columns = [col.strip() for col in market_df.columns]

# Parse dates carefully
returns_df["Date"] = pd.to_datetime(returns_df["Date"], dayfirst=True, errors="coerce")
market_df["Date"] = pd.to_datetime(market_df["Date"], errors="coerce")

returns_df = returns_df.dropna(subset=["Date"]).copy()
market_df = market_df.dropna(subset=["Date"]).copy()

returns_df = returns_df.sort_values("Date").reset_index(drop=True)
market_df = market_df.sort_values("Date").reset_index(drop=True)

# Identify stock columns
stock_cols = [col for col in returns_df.columns if col != "Date"]

# Convert returns columns to numeric
for col in stock_cols:
    returns_df[col] = pd.to_numeric(returns_df[col], errors="coerce")

market_df["Market_Return"] = pd.to_numeric(market_df["Market_Return"], errors="coerce")

# Merge market return into stock returns
df = pd.merge(returns_df, market_df[["Date", "Market_Return"]], on="Date", how="inner")

# ==========================================
# 3. PARAMETERS
# ==========================================
windows = [20, 50]

# ==========================================
# 4. CALCULATE DAILY COUPLING METRICS
# ==========================================
all_stock_frames = []
summary_rows = []

for stock in stock_cols:
    temp = df[["Date", stock, "Market_Return"]].copy()
    temp = temp.rename(columns={stock: "Return"})

    # Rolling correlation
    for w in windows:
        temp[f"Rolling_Corr_{w}"] = temp["Return"].rolling(w).corr(temp["Market_Return"])

        # Rolling beta = rolling covariance / rolling variance of market
        rolling_cov = temp["Return"].rolling(w).cov(temp["Market_Return"])
        rolling_var_mkt = temp["Market_Return"].rolling(w).var()

        temp[f"Beta_{w}"] = np.where(rolling_var_mkt != 0, rolling_cov / rolling_var_mkt, np.nan)

        # Tracking error = rolling std of active return
        active_return = temp["Return"] - temp["Market_Return"]
        temp[f"Tracking_Error_{w}"] = active_return.rolling(w).std()

    temp["Stock"] = stock
    all_stock_frames.append(temp)

    # Summary row
    summary_rows.append({
        "Stock": stock,
        "Avg_Corr_20": temp["Rolling_Corr_20"].mean(skipna=True),
        "Avg_Corr_50": temp["Rolling_Corr_50"].mean(skipna=True),
        "Avg_Beta_20": temp["Beta_20"].mean(skipna=True),
        "Avg_Beta_50": temp["Beta_50"].mean(skipna=True),
        "Avg_Tracking_Error_20": temp["Tracking_Error_20"].mean(skipna=True),
        "Avg_Tracking_Error_50": temp["Tracking_Error_50"].mean(skipna=True),
        "Valid_Return_Obs": temp["Return"].notna().sum()
    })

# Combine all stocks into one long dataframe
daily_coupling_df = pd.concat(all_stock_frames, ignore_index=True)

# Reorder columns
daily_coupling_df = daily_coupling_df[
    [
        "Date", "Stock", "Return", "Market_Return",
        "Rolling_Corr_20", "Rolling_Corr_50",
        "Beta_20", "Beta_50",
        "Tracking_Error_20", "Tracking_Error_50"
    ]
]

summary_df = pd.DataFrame(summary_rows)

# ==========================================
# 5. SAVE OUTPUTS
# ==========================================
daily_coupling_df.to_csv(daily_output_file, index=False)
summary_df.to_csv(summary_output_file, index=False)

# ==========================================
# 6. PRINT SUMMARY
# ==========================================
print("Step 2 complete.\n")
print(f"Saved daily file: {daily_output_file}")
print(f"Saved summary file: {summary_output_file}\n")

print("Summary preview:")
print(summary_df.head())

print("\nOverall:")
print(f"Number of stocks processed: {len(stock_cols)}")
print(f"Daily coupling rows: {len(daily_coupling_df)}")