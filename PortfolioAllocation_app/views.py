# Create your views here.
import os
import json
import pandas as pd
import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Asset, PortfolioAllocation
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.http import  HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import pandas_ta as ta


from .functions1 import (
    calculate_stats, create_graph, dynamic_allocation, normalize_weights
)
from .functions2 import fetch_stock_data, fetch_news

# Set the path for media storage
MEDIA_ROOT = "media"
csv_file_name = 'Stock_data.csv'
file_path = os.path.join(MEDIA_ROOT, csv_file_name)

# View function for portfolio allocation

@csrf_exempt  
def portfolio_allocation(request):
    if request.method == 'POST':
        try:
            # Parse the JSON request body
            body_data = json.loads(request.body.decode('utf-8'))
            initial_capital = body_data.get('initial_capital')
            risk_aversion = body_data.get('risk_aversion')

            # Validate required fields
            if initial_capital is None or risk_aversion is None:
                return JsonResponse({'error': 'Initial capital and risk aversion must be provided.'}, status=400)

            # Load stock data from CSV
            data = pd.read_csv(file_path, index_col="Date", parse_dates=True).asfreq('B')

            # Get selected assets and validate their existence in the DataFrame
            selected_assets = body_data.get('assets', [])
            missing_assets = [asset for asset in selected_assets if asset not in data.columns]
            if missing_assets:
                return JsonResponse({'error': f"Assets not found in data: {', '.join(missing_assets)}"}, status=400)

            data = data[selected_assets]

            # Retrieve and normalize initial weights for selected assets
            initial_weights = []
            for asset in selected_assets:
                weight_key = f'weight_{asset}'
                weight_value = body_data.get(weight_key)
                if weight_value is None:
                    return JsonResponse({'error': f'Weight for asset {asset} is missing.'}, status=400)
                initial_weights.append(float(weight_value))
            initial_weights = normalize_weights(np.array(initial_weights))

            # Create a graph from the input edges
            edges = body_data.get('edges', [])
            G = create_graph(edges, selected_assets)

            # Calculate annualized returns, volatility, and average volume
            annualized_returns, volatility, average_volume = calculate_stats(data)

            # Perform dynamic allocation
            positions, new_weights = dynamic_allocation(data, G, initial_capital, initial_weights, risk_aversion, selected_assets)

            # Save portfolio allocations to the database and prepare the response data
            allocation_data = []
            for asset_name, new_position, new_weight in zip(selected_assets, positions, new_weights):
                asset, created = Asset.objects.get_or_create(name=asset_name, symbol=asset_name)
                PortfolioAllocation.objects.create(
                    asset=asset,
                    initial_capital=initial_capital,
                    risk_aversion=risk_aversion,
                    weight=new_weight,
                    new_position=new_position,
                    new_weight=new_weight
                )
                
                # Add allocation details to response data
                allocation_data.append({
                    'company_name': asset_name,
                    'new_position': new_position,
                    'new_weight': new_weight
                })

            # Prepare response data
            response_data = {
                'annualized_returns': annualized_returns.to_dict(),
                'volatility': volatility.to_dict(),
                'allocations': allocation_data,
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# View function for dashboard allocation

@csrf_exempt  
def dashboard_allocation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            symbol = data['symbol']
            
            # Fetch stock data and news using the provided symbol
            stock_data = fetch_stock_data(symbol)
            # news_items = fetch_news(symbol)

            # Validate the fetched stock data
            if stock_data is None:
                return JsonResponse({'status': 'error', 'message': 'Invalid stock symbol or no data available.'}, status=400)

            # Format the stock data for the response
            formatted_stock_data = stock_data.reset_index().to_dict(orient='records')

            # Call the function to generate the graph and get the file path
            graph_url = generate_stock_graph(stock_data,symbol)

            return JsonResponse({
                'status': 'success',
                'data': {
                    # 'stock_data': formatted_stock_data,
                    # 'news': news_items,
                    'graph_url': graph_url  # Send the graph URL in the response
                }
            })

        except KeyError:
            return JsonResponse({'status': 'error', 'message': 'Invalid input.'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


# Function to generate stock graph and save as PNG file
def generate_stock_graph(df,symbol):
    # Calculate Super Trend
    multiplier = 3
    atr_length = 14

    # Calculate ATR (Average True Range)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=atr_length)

    # Calculate the Super Trend
    df['Upper Basic'] = (df['High'] + df['Low']) / 2 + (multiplier * df['ATR'])
    df['Lower Basic'] = (df['High'] + df['Low']) / 2 - (multiplier * df['ATR'])

    df['SuperTrend'] = np.nan
    for i in range(1, len(df)):
        if df['Close'][i] > df['Upper Basic'][i-1]:
            df['SuperTrend'][i] = df['Upper Basic'][i]
        else:
            df['SuperTrend'][i] = df['Lower Basic'][i]

    # Calculate SMAs and EMAs
    df['SMA20'] = ta.sma(df['Close'], length=20)
    df['SMA50'] = ta.sma(df['Close'], length=50)
    df['EMA20'] = ta.ema(df['Close'], length=20)
    df['EMA50'] = ta.ema(df['Close'], length=50)

    # Calculate RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)

    # Create the plot
    plt.figure(figsize=(14, 8))

    # Plot Close price (Trace 0)
    plt.plot(df.index, df['Close'], label='Close Price', color='#2E8B57', linewidth=2, alpha=0.8)

    # Plot RSI
    plt.plot(df.index, df['RSI'], label='RSI', color='#FF6347', linestyle='--', linewidth=2)

    # Plot Super Trend
    plt.plot(df.index, df['SuperTrend'], label='Super Trend', color='#1E90FF', linewidth=2)

    # Plot SMA 20
    plt.plot(df.index, df['SMA20'], label='SMA 20', color='#FFD700', linewidth=2)

    # Plot SMA 50
    plt.plot(df.index, df['SMA50'], label='SMA 50', color='#00BFFF', linewidth=2)

    # Plot EMA 20
    plt.plot(df.index, df['EMA20'], label='EMA 20', color='#32CD32', linewidth=2)

    # Plot EMA 50
    plt.plot(df.index, df['EMA50'], label='EMA 50', color='#8A2BE2', linewidth=2)

    # Add labels and title
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(f'{symbol} Stock Data with Indicators')
    plt.legend()

    # Add grid for better readability
    plt.grid(True)

    # Save the plot to a file
    media_path = os.path.join(settings.MEDIA_ROOT, 'graphs')
    if not os.path.exists(media_path):
        os.makedirs(media_path)
    
    # Generate a unique filename
    file_path = os.path.join(media_path, f'{symbol}_stock_graph.png')
    
    plt.savefig(file_path)
    plt.close()

    # Return the URL to the saved image
    return os.path.join(settings.MEDIA_URL, 'graphs', f'{symbol}_stock_graph.png')
# ---input1
#  {
#    "initial_capital": 100000,
#    "risk_aversion": 0.5,
#    "assets": ["RELIANCE.BO", "TCS.BO", "HDFCBANK.BO"],
#    "weight_RELIANCE.BO": 0.4,
#    "weight_TCS.BO": 0.3,
#    "weight_HDFCBANK.BO": 0.3,
#    "edges": [
#      ["RELIANCE.BO", "TCS.BO"],
#      ["TCS.BO", "HDFCBANK.BO"]
#    ]
# }
# ---input2
# {
#   "symbol": "MSFT"
# }