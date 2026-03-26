import os
import pandas as pd
import numpy as np

# ==========================================
# 1. PATHS
# ==========================================
input_file = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\master_returns_refined_v2.csv"
output_folder = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\analysis_00"

os.makedirs(output_folder, exist_ok=True)

market_output_file = os.path.join(output_folder, "daily_market_state.csv")

# ==========================================
# 2. LOAD MASTER RETURNS
# ==========================================
df = pd.read_csv(input_file)

# Clean column names
df.columns = [col.strip() for col in df.columns]

# Parse Date properly (your file is dd/mm/yyyy)
if "Date" not in df.columns:
    raise ValueError("Date column not found.")

df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["Date"]).copy()
df = df.sort_values("Date").reset_index(drop=True)

# Identify stock columns
stock_cols = [col for col in df.columns if col != "Date"]

# Convert all stock columns to numeric
for col in stock_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ==========================================
# 3. DAILY MARKET RETURN
# ==========================================
# Mean across all available stocks on each date
df["Market_Return"] = df[stock_cols].mean(axis=1, skipna=True)

# ==========================================
# 4. CROSS-SECTIONAL DISPERSION
# ==========================================
# Std deviation across all available stocks on each date
df["Cross_Sectional_Dispersion"] = df[stock_cols].std(axis=1, skipna=True)

# ==========================================
# 5. VALID STOCK COUNT
# ==========================================
df["Valid_Stock_Count"] = df[stock_cols].notna().sum(axis=1)

# ==========================================
# 6. FINAL OUTPUT
# ==========================================
market_df = df[[
    "Date",
    "Market_Return",
    "Cross_Sectional_Dispersion",
    "Valid_Stock_Count"
]].copy()

market_df.to_csv(market_output_file, index=False)

# ==========================================
# 7. PRINT SUMMARY
# ==========================================
print("Step 1 complete.\n")
print(f"Saved file: {market_output_file}\n")

print("Preview:")
print(market_df.head())

print("\nSummary:")
print(f"Total dates: {len(market_df)}")
print(f"Average market return: {market_df['Market_Return'].mean():.4f}")
print(f"Average cross-sectional dispersion: {market_df['Cross_Sectional_Dispersion'].mean():.4f}")
print(f"Minimum valid stock count: {market_df['Valid_Stock_Count'].min()}")
print(f"Maximum valid stock count: {market_df['Valid_Stock_Count'].max()}")