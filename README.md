# Stock Portfolio Tracker with Sentiment Analysis

## Overview
This project is a Stock Portfolio Tracker that integrates real-time stock price tracking and sentiment analysis of news articles related to stocks. Users can send emails based on target values. Built with Streamlit, pandas, and yfinance, the application provides users with insights into stock performance and associated market sentiment.

## Features
- **Portfolio**: Visualise portfolio value over time, add, remove, export portfolio. Visualise individual stock performance. Current holdings and purchase history tables. Watchlist feature, to add your most important stocks.
- **News Sentiment Analysis**: Analyze sentiment from news articles about a given stock.
- **Notify me**: Email alerts when stock prices hit target values.

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/brengall99/stock_portfolio_tracker.git
   cd stock_portfolio_tracker
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up your **NewsAPI** key:
   - Get an API key from [NewsAPI](https://newsapi.org/)
   - Create a `.env` file and add:
     ```env
     NEWS_API_KEY="your_api_key_here"
     ```
5. If you're using a **Gmail** account to send email alerts, you'll need an **App Password** instead of your normal password:
   - Go to **[Google Account Security](https://myaccount.google.com/security)**.
   - Enable **2-Step Verification** if not already enabled.
   - Scroll to **App passwords** and click **Generate App Password**.
   - Select "Mail" as the app and "Other" as the device, then generate a password.
   - Copy the password and use it in your `.env` file as `EMAIL_PASSWORD`, along with your gmail username as `EMAIL_USER`.

## Usage
1. Run the Streamlit app:
   ```sh
   streamlit run Portfolio.py
   ```

## Future Improvements
I want the portfolio to actually reflect reality when a new stock is added, so it will be at 0 before the stock is purchased, then will jump up to the stock*quantity value then continue on tracking the price. Currently it only shows an aggregate of the stocks you have added to your portfolio, and doesn't take purchase date into account for the "Portfolio Value Over Time" section.

## Examples

### Portfolio
![Bildschirmfoto 2025-02-09 um 22 02 10](https://github.com/user-attachments/assets/30cb9fe4-81a4-44af-9105-a458a4278eda)
![Bildschirmfoto 2025-02-09 um 22 02 02](https://github.com/user-attachments/assets/9b14b17a-cca3-41d7-82e9-a0b8c2425361)
![Bildschirmfoto 2025-02-09 um 22 03 47](https://github.com/user-attachments/assets/c799dad0-386e-44e3-bdd7-9fe785b0f2db)

### Sentiment Analysis
![Bildschirmfoto 2025-02-09 um 21 50 33](https://github.com/user-attachments/assets/b0e24fe7-d563-45da-9563-b87760ee2171)

### Notify Me
![Bildschirmfoto 2025-02-09 um 21 39 52](https://github.com/user-attachments/assets/e7e4b216-725b-4269-b2a9-2fb2f8cc3ec7)
<img width="656" alt="Bildschirmfoto 2025-02-09 um 21 39 21" src="https://github.com/user-attachments/assets/5ce98868-3a69-4d77-994f-0ff47b0a773d" />
