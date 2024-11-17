import numpy as np
import pandas as pd
import networkx as nx
from statsmodels.tsa.arima.model import ARIMA


# Function to calculate historical returns, volatility, and average volume
def calculate_stats(data):
    data = data.dropna()
    returns = data.pct_change().dropna()
    annualized_returns = returns.mean() * 252
    volatility = returns.std() * np.sqrt(252)
    average_volume = data['Volume'].mean() if 'Volume' in data.columns else None 
    return annualized_returns, volatility, average_volume

# Function to simulate random volume data
def simulate_volume(data):
    np.random.seed(0)
    volume = np.random.randint(1000, 10000, size=len(data))
    data['Volume'] = volume
    return data

# Function to predict price using ARIMA
def predict_price(data, order=(5, 1, 0)):
    try:
        model = ARIMA(data, order=order)
        model_fit = model.fit()
        prediction = model_fit.forecast(steps=1).iloc[0]

    except Exception as e:
        print(f"Error predicting price for {data.name}: {e}")
        prediction = data.iloc[-1]
    return prediction

# Ripple effect simulation
def ripple_effect(graph, changes):
    ripple_impact = {}
    for node, change in changes.items():
        for neighbor in nx.single_source_shortest_path(graph, node):
            ripple_impact[neighbor] = ripple_impact.get(neighbor, 0) + change
    return ripple_impact

# Function to calculate correlation matrix
def calculate_correlation(data):
    return data.pct_change(fill_method=None).corr()

# Adjust exposure based on ripple effect
def adjust_allocation(weights, ripple_impact, risk_increase, assets, correlation_matrix):
    for asset in ripple_impact:
        if asset in assets:
            index = assets.index(asset)
            avg_correlation = correlation_matrix.loc[asset].mean()
            weights[index] = max(0, weights[index] - risk_increase * ripple_impact[asset] * avg_correlation)
    return weights

# Normalize weights
def normalize_weights(weights):
    total_weight = np.sum(weights)
    if total_weight == 0:
        raise ValueError("Weights cannot sum to zero.")
    return weights / total_weight

# Create graph for ripple effect
def create_graph(edges, assets):
    G = nx.Graph()
    G.add_edges_from(edges)
    for asset in assets:
        G.add_node(asset)
    return G

# Dynamic asset allocation function
def dynamic_allocation(data, graph, initial_capital, weights, risk_aversion, assets, order=(5, 1, 0)):
    predicted_changes = {}
    for asset in assets:
        predicted_change = predict_price(data[asset], order=order)
        change_percentage = (predicted_change - data[asset].iloc[-1]) / data[asset].iloc[-1]
        predicted_changes[asset] = change_percentage
    ripple_impact = ripple_effect(graph, predicted_changes)
    correlation_matrix = calculate_correlation(data[assets])
    risk_increase = risk_aversion * 0.1
    new_weights = adjust_allocation(weights.copy(), ripple_impact, risk_increase, assets, correlation_matrix)
    new_weights = normalize_weights(new_weights)
    positions = (new_weights * initial_capital) / data[assets].iloc[-1, :]
    return positions, new_weights


