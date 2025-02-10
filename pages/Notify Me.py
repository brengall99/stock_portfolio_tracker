import streamlit as st
import yfinance as yf
import pandas as pd
from utils.email_alerts import send_email_alert

# initialise session state
if "alerts" not in st.session_state:
    st.session_state.alerts = {}  # active alerts
if "sent_alerts" not in st.session_state:
    st.session_state.sent_alerts = []  # list of sent alerts
if "email" not in st.session_state:
    st.session_state.email = ""

st.set_page_config(page_title="Stock Alerts", layout="wide", page_icon="🔔")
st.title("Notify Me")
st.write("Set target prices and get notified when your stocks reach them.")

# sidebar: email input
st.sidebar.header("Notification Settings")
st.session_state.email = st.sidebar.text_input("Enter your email for alerts", st.session_state.email)

st.header("Price Alerts")

# dialog box for adding alerts
@st.dialog("Add a Price Alert")
def add_alert_dialog() -> None:
    col1, col2 = st.columns([2, 1])
    with col1:
        new_stock = st.text_input("Stock Symbol", max_chars=10).upper()
    with col2:
        target_price = st.number_input("Target Price ($)", min_value=0.01, format="%.2f")

    alert_type = st.radio("Alert Type", ["Above", "Below"], horizontal=True)

    if st.button("Add Alert"):
        if new_stock and target_price:
            st.session_state.alerts[new_stock] = {"price": target_price, "type": alert_type}
            st.rerun()

st.button("➕ Add Alert", on_click=add_alert_dialog)

# remove alerts
if st.session_state.alerts:
    col1, col2 = st.columns([3, 1])
    with col1:
        remove_stock = st.selectbox("Remove Alert", list(st.session_state.alerts.keys()))
    with col2:
        if st.button("Remove"):
            st.session_state.alerts.pop(remove_stock, None)
            st.rerun()

st.divider()

# function to fetch stock prices
def get_stock_price(ticker: str) -> float:
    stock = yf.Ticker(ticker)
    price = stock.info.get("regularMarketPrice")

    if price is None:  # if regularMarketPrice is unavailable, fetch last closing price
        hist = stock.history(period="1d")
        if not hist.empty:
            price = hist["Close"].iloc[-1]  # use last available closing price
    return price

# display active stock alerts
if st.session_state.alerts:
    st.subheader("Active Alerts")

    for stock, alert_data in list(st.session_state.alerts.items()):
        target = alert_data["price"]
        alert_type = alert_data["type"]
        price = get_stock_price(stock)

        col1, col2 = st.columns([2, 1])
        col1.metric(stock, f"${price:.2f}" if price else "N/A", f"Target {alert_type}: ${target}")

        # check alert condition
        if price is not None:
            if (alert_type == "Above" and price >= target) or (alert_type == "Below" and price <= target):
                if st.session_state.email:
                    send_email_alert(st.session_state.email, f"{stock}", price, target)
                    st.success(f"Alert sent for {stock} to {st.session_state.email}!")

                st.session_state.sent_alerts.append(
                    {"stock": stock, "target": target, "alert_type": alert_type, "triggered_at": price}
                )
                del st.session_state.alerts[stock]  # remove from active alerts
                st.rerun()

else:
    st.info("No active alerts. Add stocks to track price targets.")

st.divider()

# display sent alerts
if st.session_state.sent_alerts:
    st.subheader("Sent Alerts")
    sent_df = pd.DataFrame(st.session_state.sent_alerts).rename(
        columns={
            "stock": "Stock",
            "target": "Target Price",
            "alert_type": "Alert Type",
            "triggered_at": "Triggered at Price"
        }
    )
    st.dataframe(sent_df, use_container_width=True, hide_index=True)
