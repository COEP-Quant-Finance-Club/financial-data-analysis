import os
import pandas as pd
import numpy as np

# ==========================================
# 1. PATHS
# ==========================================
returns_file = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\master_returns_refined_v2.csv"
output_folder = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\Entropy\Entropy data"

os.makedirs(output_folder, exist_ok=True)

daily_output_file = os.path.join(output_folder, "stock_entropy_daily.csv")
summary_output_file = os.path.join(output_folder, "stock_entropy_summary.csv")

# ==========================================
# 2. SETTINGS
# ==========================================
windows = [20, 50]
num_bins = 10

# ==========================================
# 3. LOAD RETURNS FILE
# ==========================================
df = pd.read_csv(returns_file)
df.columns = [col.strip() for col in df.columns]

if "Date" not in df.columns:
    raise ValueError("Date column not found in returns file.")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
df = df.dropna(subset=["Date"]).copy()
df = df.sort_values("Date").reset_index(drop=True)

stock_cols = [col for col in df.columns if col != "Date"]

for col in stock_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ==========================================
# 4. ENTROPY FUNCTION
# ==========================================
def shannon_entropy(series, bins=10):
    values = pd.Series(series).dropna().values

    if len(values) < 2:
        return np.nan

    # If all values are identical, entropy is 0
    if np.all(values == values[0]):
        return 0.0

    counts, _ = np.histogram(values, bins=bins)
    probs = counts / counts.sum()

    # Remove zero probabilities before log
    probs = probs[probs > 0]

    entropy = -np.sum(probs * np.log(probs))
    return entropy

# ==========================================
# 5. COMPUTE ROLLING ENTROPY
# ==========================================
all_stock_frames = []
summary_rows = []

for stock in stock_cols:
    temp = df[["Date", stock]].copy()
    temp = temp.rename(columns={stock: "Return"})

    for w in windows:
        temp[f"Entropy_{w}"] = temp["Return"].rolling(window=w).apply(
            lambda x: shannon_entropy(x, bins=num_bins),
            raw=False
        )

    temp["Stock"] = stock
    all_stock_frames.append(temp)

    summary_rows.append({
        "Stock": stock,
        "Avg_Entropy_20": temp["Entropy_20"].mean(skipna=True),
        "Avg_Entropy_50": temp["Entropy_50"].mean(skipna=True),
        "Valid_Return_Obs": temp["Return"].notna().sum()
    })

# ==========================================
# 6. COMBINE OUTPUTS
# ==========================================
daily_entropy_df = pd.concat(all_stock_frames, ignore_index=True)

daily_entropy_df = daily_entropy_df[
    ["Date", "Stock", "Return", "Entropy_20", "Entropy_50"]
]

summary_df = pd.DataFrame(summary_rows)

# ==========================================
# 7. SAVE FILES
# ==========================================
daily_entropy_df.to_csv(daily_output_file, index=False)
summary_df.to_csv(summary_output_file, index=False)

# ==========================================
# 8. PRINT SUMMARY
# ==========================================
print("Step 3 complete.\n")
print(f"Saved daily entropy file: {daily_output_file}")
print(f"Saved summary entropy file: {summary_output_file}\n")

print("Summary preview:")
print(summary_df.head())

print("\nOverall:")
print(f"Number of stocks processed: {len(stock_cols)}")
print(f"Daily entropy rows: {len(daily_entropy_df)}")