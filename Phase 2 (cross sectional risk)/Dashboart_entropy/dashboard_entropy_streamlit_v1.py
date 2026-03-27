import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# =========================================================
# FULL PATHS - EDIT THESE
# =========================================================
MARKET_FILE = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\Dashboard_00\daily_market_state.csv"
DAILY_FILE = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\analysis_01\stock_market_coupling_daily.csv"
SUMMARY_FILE = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\Entropy\Entropy data phase 2\stock_market_coupling_entropy_summary.csv"

# Folder containing per-stock OHLC CSV files for candlestick chart
OHLC_FOLDER = r"E:\QUANT FINANCE COEP\FDAS\Phase 1\fetching\yahoo_ohlcv_200_to_400"

# Folder where saved graph images will go
SAVE_FOLDER = r"E:\QUANT FINANCE COEP\FDAS\Phase 2_cross_sectional_risk\Dashboard_00\saved_graphs_streamlit"
os.makedirs(SAVE_FOLDER, exist_ok=True)

st.set_page_config(page_title="Person 3 Dashboard", layout="wide")

summary_metrics = [
    "Avg_Corr_20", "Avg_Corr_50",
    "Avg_Beta_20", "Avg_Beta_50",
    "Avg_Tracking_Error_20", "Avg_Tracking_Error_50",
    "Avg_Entropy_20", "Avg_Entropy_50"
]

comparison_metrics = [
    "Return",
    "Rolling_Corr_20", "Rolling_Corr_50",
    "Beta_20", "Beta_50",
    "Tracking_Error_20", "Tracking_Error_50"
]


@st.cache_data
def load_csv(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path)


@st.cache_data
def load_data():
    market_df = load_csv(MARKET_FILE)
    daily_df = load_csv(DAILY_FILE)
    summary_df = load_csv(SUMMARY_FILE)

    market_df.columns = [c.strip() for c in market_df.columns]
    daily_df.columns = [c.strip() for c in daily_df.columns]
    summary_df.columns = [c.strip() for c in summary_df.columns]

    market_df["Date"] = pd.to_datetime(market_df["Date"], errors="coerce")
    daily_df["Date"] = pd.to_datetime(daily_df["Date"], errors="coerce")

    market_df = market_df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    daily_df = daily_df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

    return market_df, daily_df, summary_df


@st.cache_data
def try_load_ohlc(stock_name: str):
    candidates = [
        f"{stock_name}.csv",
        f"{stock_name}_processed.csv",
        f"{stock_name}_processed_processed.csv",
    ]

    for fname in candidates:
        path = os.path.join(OHLC_FOLDER, fname)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = [c.strip() for c in df.columns]

            required_cols = {"Date", "Open", "High", "Low", "Close"}
            if not required_cols.issubset(set(df.columns)):
                continue

            df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)

            for col in ["Open", "High", "Low", "Close"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            df = df.dropna(subset=["Date", "Open", "High", "Low", "Close"]).copy()
            df = df.sort_values("Date").reset_index(drop=True)
            return df, path

    return None, None


market_df, daily_df, summary_df = load_data()
stock_list = sorted(daily_df["Stock"].dropna().unique().tolist())

avg_coupling_df = (
    daily_df.groupby("Date", as_index=False)[
        ["Rolling_Corr_20", "Rolling_Corr_50", "Beta_20", "Beta_50", "Tracking_Error_20", "Tracking_Error_50"]
    ]
    .mean()
    .sort_values("Date")
)


def save_figure(fig, base_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SAVE_FOLDER, f"{base_name}_{timestamp}.png")
    pio.write_image(fig, path, width=1600, height=900, scale=2)
    return path


def show_and_save(fig, key, title):
    st.plotly_chart(
        fig,
        width="stretch",
        config={
            "displaylogo": False,
            "toImageButtonOptions": {
                "format": "png",
                "filename": title.replace(" ", "_").lower(),
                "height": 900,
                "width": 1600,
                "scale": 2
            }
        }
    )
    if st.button(f"Save {title}", key=f"save_{key}"):
        st.success(f"Saved: {save_figure(fig, key)}")


st.title("Person 3 - Systemic Risk Dashboard")
st.caption("Run with: streamlit run dashboard_streamlit_v6.py")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Market Overview", "Rankings", "Scatter", "Deep Dive", "Compare Stocks"
])

with tab1:
    metric = st.selectbox(
        "Market metric",
        ["Market_Return", "Cross_Sectional_Dispersion", "Valid_Stock_Count"]
    )

    fig = px.line(
        market_df,
        x="Date",
        y=metric,
        title=f"{metric} Over Time",
        template="plotly_white"
    )
    show_and_save(fig, "market_metric", metric)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=market_df["Date"],
        y=market_df["Market_Return"],
        mode="lines",
        name="Market Return"
    ))
    fig2.add_trace(go.Scatter(
        x=market_df["Date"],
        y=market_df["Cross_Sectional_Dispersion"],
        mode="lines",
        name="Dispersion",
        yaxis="y2"
    ))
    fig2.update_layout(
        template="plotly_white",
        title="Market Return and Dispersion",
        yaxis2=dict(overlaying="y", side="right")
    )
    show_and_save(fig2, "market_dual", "Market Return and Dispersion")

    coupling_metric = st.selectbox(
        "Average coupling metric",
        ["Rolling_Corr_20", "Rolling_Corr_50", "Beta_20", "Beta_50", "Tracking_Error_20", "Tracking_Error_50"]
    )
    fig3 = px.line(
        avg_coupling_df,
        x="Date",
        y=coupling_metric,
        title=f"Average {coupling_metric}",
        template="plotly_white"
    )
    show_and_save(fig3, "avg_coupling", coupling_metric)

with tab2:
    metric = st.selectbox("Ranking metric", summary_metrics)
    n = st.slider("Number of stocks", 5, 50, 20, 5)

    temp = summary_df[["Stock", metric]].dropna()
    top_df = temp.sort_values(metric, ascending=False).head(n)
    bottom_df = temp.sort_values(metric, ascending=True).head(n)

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            top_df,
            x=metric,
            y="Stock",
            orientation="h",
            title=f"Top {n} by {metric}",
            template="plotly_white"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_and_save(fig, "top_rank", "Top Ranking")

    with c2:
        fig = px.bar(
            bottom_df,
            x=metric,
            y="Stock",
            orientation="h",
            title=f"Bottom {n} by {metric}",
            template="plotly_white"
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show_and_save(fig, "bottom_rank", "Bottom Ranking")

with tab3:
    x_metric = st.selectbox("X-axis", summary_metrics, index=0)
    y_metric = st.selectbox("Y-axis", summary_metrics, index=2)

    fig = px.scatter(
        summary_df,
        x=x_metric,
        y=y_metric,
        hover_data=["Stock"],
        title=f"{y_metric} vs {x_metric}",
        template="plotly_white"
    )
    show_and_save(fig, "scatter", "Scatter Plot")

with tab4:
    stock = st.selectbox("Stock", stock_list)
    stock_df = daily_df[daily_df["Stock"] == stock].copy().sort_values("Date")

    st.subheader("Price vs Time (Candlestick)")
    ohlc_df, ohlc_path = try_load_ohlc(stock)

    if ohlc_df is not None:
        candle = go.Figure(data=[go.Candlestick(
            x=ohlc_df["Date"],
            open=ohlc_df["Open"],
            high=ohlc_df["High"],
            low=ohlc_df["Low"],
            close=ohlc_df["Close"],
            name=stock
        )])
        candle.update_layout(
            title=f"{stock} Candlestick Chart",
            template="plotly_white",
            xaxis_rangeslider_visible=True
        )
        show_and_save(candle, f"deep_candle_{stock}", f"{stock} Candlestick")
        st.caption(f"Loaded OHLC file: {ohlc_path}")
    else:
        st.info("No OHLC file found for this stock in OHLC_FOLDER.")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=stock_df["Date"],
        y=stock_df["Return"],
        mode="lines",
        name=f"{stock} Return"
    ))
    fig1.add_trace(go.Scatter(
        x=stock_df["Date"],
        y=stock_df["Market_Return"],
        mode="lines",
        name="Market Return"
    ))
    fig1.update_layout(
        title=f"{stock} Return vs Market",
        template="plotly_white"
    )
    show_and_save(fig1, "deep_return", "Deep Dive Return")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=stock_df["Date"],
        y=stock_df["Rolling_Corr_20"],
        mode="lines",
        name="Corr 20"
    ))
    fig2.add_trace(go.Scatter(
        x=stock_df["Date"],
        y=stock_df["Rolling_Corr_50"],
        mode="lines",
        name="Corr 50"
    ))
    fig2.update_layout(
        title=f"{stock} Rolling Correlation",
        template="plotly_white"
    )
    show_and_save(fig2, "deep_corr", "Deep Dive Correlation")

with tab5:
    selected = st.multiselect("Choose two or more stocks", stock_list, default=stock_list[:2])
    metric = st.selectbox("Comparison metric", comparison_metrics, index=0)
    include_market = st.checkbox("Include market return when metric is Return", value=True)

    if selected:
        filtered = daily_df[daily_df["Stock"].isin(selected)].copy().sort_values("Date")

        fig = px.line(
            filtered,
            x="Date",
            y=metric,
            color="Stock",
            title=f"{metric} Comparison",
            template="plotly_white"
        )

        if include_market and metric == "Return":
            overlay = filtered[["Date", "Market_Return"]].drop_duplicates().sort_values("Date")
            fig.add_trace(go.Scatter(
                x=overlay["Date"],
                y=overlay["Market_Return"],
                mode="lines",
                name="Market Return",
                line=dict(width=3, dash="dash")
            ))

        show_and_save(fig, "compare_stocks", "Compare Stocks")

        cols = ["Stock"] + summary_metrics + (["Valid_Return_Obs"] if "Valid_Return_Obs" in summary_df.columns else [])
        st.dataframe(
            summary_df[summary_df["Stock"].isin(selected)][cols].sort_values("Stock"),
            width="stretch"
        )
    else:
        st.info("Select at least one stock.")