import pandas as pd
import numpy as np
import os

def load_data(filepath: str) -> pd.DataFrame:
    """
    Loads CSV price data.
    Handles both 'Date' (Daily) and 'Datetime' (Intraday) columns.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found at: {filepath}")

    df = pd.read_csv(filepath)
    
    # 1. Clean Column Names (Capitalize everything: 'close' -> 'Close')
    df.columns = [c.capitalize() for c in df.columns]
    
    # 2. Parse Dates (Handle standard 'Date' OR yfinance 'Datetime')
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], utc=True) # UTC=True handles timezone issues
        df.set_index('Date', inplace=True)
    elif 'Datetime' in df.columns:
        df['Datetime'] = pd.to_datetime(df['Datetime'], utc=True)
        df.set_index('Datetime', inplace=True)
    
    # 3. Sort ensures the timeline is correct
    df.sort_index(inplace=True)
    
    return df

def generate_synthetic_data(filename='data/synthetic_data.csv', days=1000):
    """
    Generates a random walk geometric brownian motion for testing purposes
    if user does not have a CSV.
    """
    np.random.seed(42)
    dt = 1/252
    mu = 0.05
    sigma = 0.2
    
    dates = pd.date_range(start='2020-01-01', periods=days)
    price = np.zeros(days)
    price[0] = 100
    
    for t in range(1, days):
        price[t] = price[t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal())
    
    df = pd.DataFrame(index=dates)
    df['Open'] = price
    df['High'] = price * (1 + np.random.uniform(0, 0.02, days))
    df['Low']  = price * (1 - np.random.uniform(0, 0.02, days))
    df['Close'] = price # Simplify close to seed price
    df['Volume'] = np.random.randint(1000, 10000, days)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename)
    print(f"Synthetic data created at {filename}")