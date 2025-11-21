import yfinance as yf
import pandas as pd
import os

def download_market_data(ticker, start_date=None, end_date=None):
    """
    Downloads HOURLY data from Yahoo Finance.
    Note: Yahoo limits hourly data to the last ~730 days (2 years).
    """
    print(f"Downloading {ticker} HOURLY data (Limit: approx 2 years)...")
    
    # No start/end date needed usually for intraday, yf defaults to max available
    # period="730d" gets the last 2 years of hourly data
    df = yf.download(ticker, interval="1h", period="730d", progress=False)
    
    if df.empty:
        print(f"Error: No data found for {ticker}.")
        return

    # Flatten MultiIndex columns
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Drop rows with NaN values (often happens at start/end of hourly pulls)
    df = df.dropna()
    
    filename = f"data/{ticker}_1h_data.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    df.to_csv(filename)
    print(f"Success! Hourly data saved to: {filename}")
    print(f"Rows: {len(df)}")

if __name__ == "__main__":
    # Test run: Get Bitcoin Data
    download_market_data("BTC-USD")