import os
import pandas as pd

coupling_summary_file = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\Dashboard_00\stock_market_coupling_summary.csv"
entropy_summary_file = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\Entropy\Entropy data phase 1\stock_entropy_summary.csv"

output_folder = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\Entropy\Entropy data phase 2"
os.makedirs(output_folder, exist_ok=True)

output_file = os.path.join(output_folder, "stock_market_coupling_entropy_summary.csv")

print("Coupling file exists:", os.path.exists(coupling_summary_file))
print("Entropy file exists:", os.path.exists(entropy_summary_file))

coupling_df = pd.read_csv(coupling_summary_file)
entropy_df = pd.read_csv(entropy_summary_file)

coupling_df.columns = [c.strip() for c in coupling_df.columns]
entropy_df.columns = [c.strip() for c in entropy_df.columns]

merged_df = pd.merge(
    coupling_df,
    entropy_df,
    on="Stock",
    how="outer",
    suffixes=("", "_entropy")
)

if "Valid_Return_Obs_entropy" in merged_df.columns:
    if "Valid_Return_Obs" in merged_df.columns:
        merged_df["Valid_Return_Obs"] = merged_df["Valid_Return_Obs"].fillna(
            merged_df["Valid_Return_Obs_entropy"]
        )
    else:
        merged_df["Valid_Return_Obs"] = merged_df["Valid_Return_Obs_entropy"]

    merged_df.drop(columns=["Valid_Return_Obs_entropy"], inplace=True)

merged_df.to_csv(output_file, index=False)

print("Done.")
print("Saved:", output_file)
print(merged_df.head())