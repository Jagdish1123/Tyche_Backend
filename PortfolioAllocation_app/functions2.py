import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import pandas_ta as ta  # Replacing talib with pandas-ta
import requests

# def fetch_stock_data(symbol):
#     # Download stock data from Yahoo Finance
#     try:
#         df = yf.download(symbol, period='1y', interval='1d')
#     except Exception as e:
#         return None  # Handle if the stock symbol is invalid

#     # Ensure data was downloaded
#     if df.empty:
#         return None

#     # Adding indicators using pandas-ta
#     df['RSI'] = ta.rsi(df['Close'], length=14)
#     df['MACD'], df['MACD_signal'] = ta.macd(df['Close'], fast=12, slow=26, signal=9)[['MACD_12_26_9', 'MACDs_12_26_9']]
#     df['SMA20'] = ta.sma(df['Close'], length=20)
#     df['SMA50'] = ta.sma(df['Close'], length=50)
#     df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
#     df['BB_upper'], df['BB_middle'], df['BB_lower'] = ta.bbands(df['Close'], length=20)[['BBU_20_2.0', 'BBM_20_2.0', 'BBL_20_2.0']]
#     df['SAR'] = ta.psar(df['High'], df['Low'], df['Close'])['PSARr_0.02_0.2']

#     return df

# def fetch_news(symbol):
#     api_key = 'your_newsapi_key'  # Ensure this key is from your config
#     url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}"
#     response = requests.get(url).json()

#     news_items = []
#     if 'articles' in response:
#         news_items = response['articles'][:5]  # Limiting to 5 news items

#     return news_items

# def create_dash_app():
#     app = Dash(__name__)

#     @app.callback(
#         [Output('stock-chart', 'figure'), Output('news-feed', 'children')],
#         [Input('symbol-input', 'value')]
#     )
#     def update_chart(symbol):
#         # Fetch stock data and news
#         df = fetch_stock_data(symbol)
#         if df is None:
#             return {}, html.P("Invalid stock symbol or no data available.", style={'color': 'red'})

#         news_items = fetch_news(symbol)

#         # Plotting stock data using Plotly
#         fig = go.Figure()

#         # Candlestick plot
#         fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlesticks'))

#         # Add moving averages
#         fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], mode='lines', name='SMA 20', line=dict(color='blue', width=1)))
#         fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], mode='lines', name='SMA 50', line=dict(color='orange', width=1)))

#         # Add Bollinger Bands
#         fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], mode='lines', name='BB Upper', line=dict(color='gray', width=1)))
#         fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], mode='lines', name='BB Lower', line=dict(color='gray', width=1)))

#         # Add RSI
#         fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI', line=dict(color='purple', width=1)))

#         # Add MACD
#         fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='green', width=1)))
#         fig.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], mode='lines', name='MACD Signal', line=dict(color='red', width=1)))

#         # Add ATR
#         fig.add_trace(go.Scatter(x=df.index, y=df['ATR'], mode='lines', name='ATR', line=dict(color='brown', width=1)))

#         # Add Parabolic SAR
#         fig.add_trace(go.Scatter(x=df.index, y=df['SAR'], mode='markers', name='Parabolic SAR', marker=dict(color='black', size=5)))

#         fig.update_layout(title=f'{symbol} Stock Data', xaxis_title='Date', yaxis_title='Price')

#         # Formatting news feed
#         news_content = [html.H3("Latest News")] + [
#             html.Div([html.A(article['title'], href=article['url'], target="_blank")]) for article in news_items
#         ]

#         return fig, news_content

#     # Layout of the app
#     app.layout = html.Div([
#         html.H1("Stock Market Dashboard"),
#         dcc.Input(id='symbol-input', type='text', value='AAPL', placeholder='Enter Stock Symbol'),
#         dcc.Graph(id='stock-chart'),
#         html.Div(id='news-feed')
#     ])

#     return app
# function.py
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import pandas_ta as ta  # Ensure you have pandas-ta installed

def fetch_stock_data(symbol):
    # Download stock data from Yahoo Finance
    try:
        df = yf.download(symbol, period='1y', interval='1d')
    except Exception as e:
        return None  # Handle if the stock symbol is invalid

    # Ensure data was downloaded
    if df.empty:
        return None

    # Adding indicators using pandas-ta
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['MACD'], df['MACD_signal'] = ta.macd(df['Close'], fast=12, slow=26, signal=9)[['MACD_12_26_9', 'MACDs_12_26_9']]
    df['SMA20'] = ta.sma(df['Close'], length=20)
    df['SMA50'] = ta.sma(df['Close'], length=50)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = ta.bbands(df['Close'], length=20)[['BBU_20_2.0', 'BBM_20_2.0', 'BBL_20_2.0']]
    df['SAR'] = ta.psar(df['High'], df['Low'], df['Close'])['PSARr_0.02_0.2']

    return df

def fetch_news(symbol):
    api_key = 'your_newsapi_key'  # Replace with your News API key
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}"
    response = requests.get(url).json()

    news_items = []
    if 'articles' in response:
        news_items = response['articles'][:5]  # Limiting to 5 news items

    return news_items
