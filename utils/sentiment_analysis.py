import os
import requests
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer() # initialize sia

def fetch_news(stock_symbol):
    """
    Fetches recent news headlines related to the given stock symbol from the News API.

    Args:
        stock_symbol (str): The stock symbol to search for.

    Returns:
        tuple: A pandas DataFrame containing news data, the overall sentiment score, and the overall sentiment label.
               Returns empty DataFrame, 0, and "Neutral" if there's an error or no articles are found.
    """
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&language=en&apiKey={NEWS_API_KEY}" # NewsAPI url
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])[:10] # extract articles, first 10

        news_data, sentiment_scores = [], []

        # iterate through articles to extract title, description, and url
        for article in articles:
            title = article["title"]
            description = article["description"] or ""
            url = article["url"]

            # perform sentiment analysis
            sentiment_score = sia.polarity_scores(title + " " + description)["compound"]
            sentiment_scores.append(sentiment_score)

            # sentiment label based on score
            sentiment = "Positive" if sentiment_score > 0.05 else \
                        "Negative" if sentiment_score < -0.05 else "Neutral"

            news_data.append({"Title": title, "Sentiment": sentiment, "Score": sentiment_score, "URL": url})

        # compute overall sentiment score
        overall_sentiment_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        overall_sentiment_label = "Positive" if overall_sentiment_score > 0.05 else \
                                  "Negative" if overall_sentiment_score < -0.05 else "Neutral"

        # return the news data as a pandas df and overall sentiment score and label
        return pd.DataFrame(news_data), overall_sentiment_score, overall_sentiment_label
    else:
        return pd.DataFrame(), 0, "Neutral"
