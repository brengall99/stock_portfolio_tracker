import streamlit as st
from utils.sentiment_analysis import fetch_news

st.set_page_config(page_title="Stock Sentiment", layout="wide", page_icon="📰")
st.title("Stock Sentiment Analysis")

# cache the results of the fetch_news function for 10 minutes to prevent redundant API calls
@st.cache_data(ttl=600)
def fetch_news_cached(stock_symbol: str) -> tuple:
    """Fetches news and sentiment data for a given stock symbol.

    Args:
        stock_symbol: The stock symbol to analyze (e.g., AAPL, MSFT).

    Returns:
        A tuple containing:
            - news_df: A Pandas DataFrame containing news articles and sentiment data.
            - overall_sentiment_score: The overall sentiment score (float).
            - overall_sentiment_label: The overall sentiment label (string, e.g., "Positive", "Negative", "Neutral").
    """
    return fetch_news(stock_symbol)

stock_symbol: str = st.text_input("Enter a stock symbol:", "").strip().upper()

# button for sentiment analysis
if st.button("Analyze Sentiment") and stock_symbol:

    # spinner while fetching
    with st.spinner("Fetching news..."): 
        result = fetch_news_cached(stock_symbol) 
        news_df, overall_sentiment_score, overall_sentiment_label = result 

    # if news articles are found
    if not news_df.empty:
        st.subheader(f"Recent News Sentiment for {stock_symbol}")

        # overall sentiment with some larger styling
        st.markdown(
            f"<h2 style='text-align: left; color: white;'>Overall Sentiment: {overall_sentiment_label} ({overall_sentiment_score:.2f})</h2>",
            unsafe_allow_html=True 
        )

        # sentiment icon based on the sentiment label
        news_df["Sentiment Icon"] = news_df["Sentiment"].map({
            "Positive": "🟢",
            "Neutral": "🟡",
            "Negative": "🔴"
        })

        # display the news articles
        st.dataframe(news_df[["Sentiment Icon", "Title", "Score", "URL"]], hide_index=True)

    else:
        # if nothing found
        st.warning("No news articles found. Try a different stock symbol.")