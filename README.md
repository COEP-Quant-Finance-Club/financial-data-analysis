# FDAS Project (README is Tentative and with Errors!)

phase 1: Data Acquisition & Structural Fundamentals
Goal: Master the basics of Pandas and NumPy by gathering a massive dataset.

The Big Task: Compile a master CSV file containing 5 years of daily "Adjusted Close" prices for 200 stocks (e.g., Nifty 200 ).

Key Skills to Learn:

Pandas: pd.read_csv(), df.append() (or pd.concat()), df.to_csv().

Looping with Data: Writing a loop to fetch data for 200 tickers using yfinance without crashing your script.

Handling Time: Converting strings to datetime objects using pd.to_datetime().

Deliverable: A single all_stocks_5yr.csv where columns are tickers and rows are dates.

phase 2: Vectorized Math & Data Cleaning
Goal: Stop using "for loops" for math and start using NumPy's speed.

The Big Task: Calculate the daily percentage returns for all 200 stocks at once. Identify and fix "bad data" (missing prices or 0-volume days).

Key Skills to Learn:

NumPy Vectorization: Learn why np.log(prices / prices.shift(1)) is 100x faster than a loop.

Cleaning: df.dropna(), df.fillna(method='ffill'), and identifying outliers with df.describe().

Reshaping: Using .T (transpose) and .stack() / .unstack() to view your 200 stocks differently.

Deliverable: A "Cleaned Returns" DataFrame and a summary table showing the top 5 most volatile stocks in your list.

phase 3: Statistical Distributions & Visualization
Goal: Understand if the market is "Normal" (hint: it's not) and visualize the risk.

The Big Task: Create a "Statistical Profile" for a portfolio. Compare a "Safe" stock (like HUL) vs. a "Volatile" stock (like ZOMATO) using visual tools.

Key Skills to Learn:

Distributions: Plotting Histograms to see "Fat Tails" (extreme losses).

Normality: Building a QQ-Plot to see how much a stock deviates from a normal distribution.

Rolling Windows: Use df.rolling(window=21).std() to see how "jumps" (volatility) change over time.

Deliverable: A 2x2 grid of plots for 4 chosen stocks comparing their return shapes.

phase 4: Risk Modeling & Portfolio Value at Risk (VaR)
Goal: Answer the ultimate question: "If I invest $10,000, what is the most I could lose tomorrow?"

The Big Task: Calculate the 95% Value at Risk (VaR) and Conditional VaR (Expected Shortfall) for all 200 stocks.

Key Skills to Learn:

Quantiles: Mastery of np.percentile() and df.quantile(0.05).

Scenario Analysis: Calculating "Historical VaR" (looking at the worst days in the last 5 years).

Correlation Matrices: Use df.corr() to see which stocks move together (essential for NumPy matrix practice).

Deliverable: A "Risk Dashboard" (a final CSV/Table) ranking all 200 stocks from "Safest" to "Riskiest" based on their 5% VaR.