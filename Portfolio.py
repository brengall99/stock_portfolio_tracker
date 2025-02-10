import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import date, datetime, timedelta
import pytz

# initialise session
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

st.set_page_config(page_title="Stock Portfolio Tracker", layout="wide", page_icon="💰")
st.title("Portfolio")

# fetch stock data from yfinance
def fetch_stock_data(ticker: str) -> tuple:
    """Fetches historical and current price data for a given ticker.
    Args:
        ticker (str): The stock ticker symbol (e.g., "AAPL", "MSFT").

    Returns:
        tuple: A tuple containing:
            - hist (pandas.DataFrame or None): A Pandas DataFrame containing historical stock data, 
              or None if an error occurred or no data was found.  The DataFrame typically
              includes columns like 'Open', 'High', 'Low', 'Close', 'Volume', etc.
            - current_price (float or None): The current price of the stock, or None."""
    try:
        stock = yf.Ticker(ticker)
        start_date = (datetime.today() - timedelta(days=15*365)).strftime("%Y-%m-%d") # 15 years ago
        hist = stock.history(start=start_date, end=datetime.today().strftime("%Y-%m-%d"))
        current_price = stock.fast_info.last_price 
        return hist, current_price
    
    except Exception as e: # handle potential errors during data fetching
        st.error(f"Error fetching data for {ticker}: {e}") # display error message to the user
        return None, None

st.sidebar.header("Add to Watchlist")
DEFAULT_WATCHLIST = ["AAPL", "MSFT", "TSLA", "GOOGL", "NVDA"]

# initialise watchlist
if "watchlist" not in st.session_state:
    st.session_state.watchlist = DEFAULT_WATCHLIST.copy()

# input field for adding a stock to the watchlist
ticker_input = st.sidebar.text_input("Enter Ticker Symbol", max_chars=10).upper()

# button to add stock to the watchlist
if st.sidebar.button("➕ Add to Watchlist"):
    if ticker_input: # if ticker not empty
        ticker_input = ticker_input.strip()
        if ticker_input not in st.session_state.watchlist:
            st.session_state.watchlist.append(ticker_input)
            st.sidebar.success(f"Added {ticker_input} to Watchlist!")
            st.rerun() # refresh the app with updated watchlist
        else:
            st.sidebar.warning(f"{ticker_input} is already in the Watchlist!")
    else:
        st.sidebar.warning("Please enter a ticker symbol.")

def get_stock_data(tickers: list) -> list:
    """Fetches and calculates stock price and percentage change for a list of tickers.

    This function retrieves historical and intraday stock data from yfinance. It calculates
    the percentage change based on market hours: if the market is open, it uses the change
    from today's open to the latest price; otherwise, it uses the change from yesterday's
    open to yesterday's close.

    Args:
        tickers (list): A list of stock ticker symbols (e.g., ["AAPL", "MSFT"]).

    Returns:
        list: A list of dictionaries, where each dictionary contains the following information
              for a stock:
                - "ticker": The stock ticker symbol (str).
                - "price": The latest price of the stock (float).
                - "change": The percentage change in price (float).

              Returns an empty list if no data is available."""
    
    stock_data = []
    now = datetime.now(pytz.timezone("US/Eastern"))  # use US/Eastern timezone for market hours

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d", interval="1d")  # get last 2 days' daily data

            if not hist.empty:
                # if market open today 
                market_open_today = now.weekday() < 5 and (now.hour > 9 or (now.hour == 9 and now.minute >= 30))  

                if market_open_today:  
                    today_data = stock.history(period="1d", interval="1m") # get 1-minute data for today
                    if not today_data.empty:
                        today_open = today_data["Open"].iloc[0] 
                        latest_price = today_data["Close"].iloc[-1] 
                        percent_change = ((latest_price - today_open) / today_open) * 100
                    else:
                        st.warning(f"No intraday data available for {ticker} today.")
                        continue  # if there's no data, skip this stock
                else:  
                    # market hasn't opened yet, use yesterday's open-close change
                    yesterday_open = hist["Open"].iloc[-1]
                    yesterday_close = hist["Close"].iloc[-1]
                    percent_change = ((yesterday_close - yesterday_open) / yesterday_open) * 100
                    latest_price = yesterday_close 

                stock_data.append({"ticker": ticker, "price": latest_price, "change": percent_change})
            else:
                st.warning(f"No historical data available for {ticker}.")
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")

    return stock_data

# display the watchlist with stock prices
if st.session_state.watchlist:
    stock_info = get_stock_data(st.session_state.watchlist)

    with st.sidebar:
        col1, col2 = st.columns([3, 1])
        col1.subheader("Your Watchlist")

        if "show_watchlist_info" not in st.session_state:
            st.session_state.show_watchlist_info = False

        if col2.button("ℹ️", help="Click for info"):
            st.session_state.show_watchlist_info = not st.session_state.show_watchlist_info

        if st.session_state.show_watchlist_info:
            st.info(
                "The percentage change is calculated based on:\n"
                "- **If the market is open:** (Current Price - Today's Open) / Today's Open * 100\n"
                "- **If the market hasn't opened yet:** (Yesterday's Close - Yesterday's Open) / Yesterday's Open * 100"
            )

    if stock_info: # check if stock_info is not empty
        for stock in stock_info:
            col1, col2, col3 = st.sidebar.columns([2, 1, 1])
            col1.write(f"**{stock['ticker']}**")
            col2.write(f"${stock['price']:.2f}")
            col3.write(f"**{stock['change']:.2f}%**")
    else:
        st.sidebar.info("No data available for the stocks in your watchlist.")

    # reset Watchlist button
    if st.sidebar.button("Reset Watchlist"):
        st.session_state.watchlist = DEFAULT_WATCHLIST.copy()
        st.sidebar.success("Watchlist reset to default!")
        st.rerun()
else:
    st.sidebar.info("Your watchlist is empty. Add stocks to track!")

@st.dialog("Add a Stock to Your Portfolio")  # streamlit dialog 
def add_stock() -> None:
    """Opens a dialog box to add a stock to the user's portfolio."""

    st.subheader("Add a Stock to Your Portfolio") 

    col1, col2, col3 = st.columns(3)  

    # input fields
    name: str = col1.text_input("Stock Name") 
    ticker: str = col2.text_input("Ticker Symbol", max_chars=10).upper()
    quantity: int = col3.number_input("Quantity", min_value=1, step=1) 

    col4, col5 = st.columns(2)
    buy_price: float = col4.number_input("Buy Price ($)", min_value=0.01, format="%.2f")  
    buy_date: float = col5.date_input("Buy Date", value=date.today())  

    if st.button("Add Stock"):  
        if ticker and buy_price:  # check if both ticker and buy price are provided
            hist, current_price = fetch_stock_data(ticker) 

            if current_price:  
                st.session_state.portfolio.append({  # append the stock details to the portfolio list in session state
                    "name": name,
                    "ticker": ticker,
                    "buy_price": buy_price,
                    "current_price": current_price,
                    "buy_date": buy_date.strftime("%Y-%m-%d"), 
                    "quantity": quantity
                })
                st.success(f"{name} ({ticker}) added to your portfolio!")  
                st.rerun()  # rerun app to update the portfolio display
            else:
                st.error("⚠️ Invalid ticker symbol. Please try again.") 

# **Portfolio Value Over Time**
st.subheader("Portfolio Value Over Time")

if st.session_state.portfolio:
    stock_data = {}

    # fetch historical data for all stocks in portfolio
    for stock in st.session_state.portfolio:
        hist, current_price = fetch_stock_data(stock["ticker"])
        if hist is not None:
            hist["Value"] = hist["Close"] * stock["quantity"]  # stock value per day
            stock_data[stock["ticker"]] = hist[["Value"]]

    # combine all stocks into one df, summing values per date
    if stock_data:
        df = pd.concat(stock_data.values(), axis=1).sum(axis=1).reset_index()
        df.columns = ["Date", "Total Portfolio Value"]

        # dropdown for selecting timebase
        timeframe_options = {
            "Last 30 Days": 30,
            "Last 3 Months": 90,
            "Last 6 Months": 180,
            "Last Year": 365,
            "5 Years": 365*5,
            "All Time": None
        }
        selected_timeframe = st.selectbox("Select Timeframe", list(timeframe_options.keys()))

        # filter data based on selected timeframe
        if timeframe_options[selected_timeframe]:  # if not "All Time"
            start_date = df["Date"].max() - pd.Timedelta(days=timeframe_options[selected_timeframe])
            df = df[df["Date"] >= start_date]

        # calculate overall percentage gain/loss
        if not df.empty:
            initial_value = df["Total Portfolio Value"].iloc[0]
            latest_value = df["Total Portfolio Value"].iloc[-1]
            percentage_change = ((latest_value - initial_value) / initial_value) * 100 if initial_value != 0 else 0
            st.metric(label="Overall % Change", value=f"{percentage_change:.2f}%", delta=f"{percentage_change:.2f}%")

        # create Line Chart
        fig = px.line(df, x="Date", y="Total Portfolio Value", title=f"Portfolio Value ({selected_timeframe})")
        st.plotly_chart(fig)

else:
    st.info("No stocks in portfolio. Add stocks to get started.")

# buttons for interacting with portfolio
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ Add Stock"):
        add_stock()

with col2:
    if st.button("➖ Delete Last") and st.session_state.portfolio:
        st.session_state.portfolio.pop()
        st.success("Last stock has been removed!")
        st.rerun()

with col3:
    if st.button("📥 Export Portfolio"):
        df = pd.DataFrame(st.session_state.portfolio)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📄 Download CSV", data=csv, file_name="portfolio.csv", mime="text/csv")

with col4:
    if st.button("❌ Remove All") and st.session_state.portfolio:
        st.session_state.portfolio.clear()
        st.success("All stocks have been removed!")
        st.rerun()

st.divider()

st.subheader("Idividual Stock Performance")

# **Portfolio Performance Chart**
if st.session_state.portfolio:
    stock_data = {}
    for stock in st.session_state.portfolio:
        hist, current_price = fetch_stock_data(stock["ticker"])
        if hist is not None:
            stock_data[stock["ticker"]] = hist

    if stock_data:
        df = pd.concat([df.assign(Stock=ticker) for ticker, df in stock_data.items()])
        df.reset_index(inplace=True)
        fig = px.line(df, x="Date", y="Close", color="Stock")
        st.plotly_chart(fig)
else:
    st.info("No stocks in portfolio. Add stocks to get started.")

st.divider()

# **Portfolio Table**
st.subheader("Current Holdings")

if st.session_state.portfolio:
    portfolio_df = pd.DataFrame(st.session_state.portfolio)
    portfolio_df["Total Cost"] = (portfolio_df["buy_price"] * portfolio_df["quantity"]).round(2)

    # aggregate data by ticker symbol
    portfolio_df = (
        portfolio_df.groupby(["name", "ticker"], as_index=False)
        .agg({
            "quantity": "sum", 
            "Total Cost": "sum",  
            "current_price": "last", 
            "buy_date": "first",  
            "buy_price": "first"  
        })
    )

    # weighted average buy price
    portfolio_df["avg_buy_price"] = (portfolio_df["Total Cost"] / portfolio_df["quantity"]).round(2)

    # reorder columns
    portfolio_df = portfolio_df[["name", "ticker", "avg_buy_price", "current_price", "quantity", "Total Cost"]].rename(
        columns={
            "name": "Stock",
            "ticker": "Ticker",
            "avg_buy_price": "Avg Buy Price (USD)",
            "current_price": "Current Price (USD)",
            "quantity": "Quantity",
            "Total Cost": "Total Cost (USD)"
        }
    )

    # display df without index and full width
    st.data_editor(portfolio_df, 
        hide_index=True, 
        use_container_width=True, 
        column_config={col: st.column_config.Column(width="small") for col in portfolio_df.columns})
else:
    st.info("No stocks in portfolio. Add stocks to get started.")

st.divider()

# **Purchases Table**
st.subheader("Purchase History")

if st.session_state.portfolio:
    purchases_df = pd.DataFrame(st.session_state.portfolio)
    purchases_df["Profit %"] = (((purchases_df["current_price"] - purchases_df["buy_price"]) / purchases_df["buy_price"]) * 100).round(2)
    
    purchases_df = purchases_df[["name", "ticker", "buy_price", "buy_date", "quantity", "Profit %"]].rename(
        columns={
            "name": "Stock",
            "ticker": "Ticker",
            "buy_price": "Buy Price (USD)",
            "buy_date": "Buy Date",
            "quantity": "Quantity",
            "Profit %": "Profit (%)"
        }
    )

    # display df without index and full width
    st.data_editor(purchases_df, 
        hide_index=True, 
        use_container_width=True, 
        column_config={col: st.column_config.Column(width="small") for col in portfolio_df.columns})
else:
    st.info("No purchases recorded.")