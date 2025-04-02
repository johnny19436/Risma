#!/usr/bin/env python3
import sys
import pandas as pd
import yfinance as yf
import os

def update_csv(csv_file, symbol):
    # Try to load the CSV file; if empty or missing, create a new DataFrame.
    try:
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        df = pd.DataFrame()

    # If the symbol is already present, do nothing.
    if symbol in df.columns:
        print(f"Symbol {symbol} already exists in CSV.")
        sys.exit(0)
    
    # Download historical data for the symbol.
    try:
        data = yf.download(symbol, start='2022-01-01', end='2024-01-01', auto_adjust=True)['Close']
    except Exception as e:
        print(f"Error downloading data for {symbol}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check that data was downloaded.
    if data.empty:
        print(f"No data downloaded for symbol: {symbol}", file=sys.stderr)
        sys.exit(1)
    
    # If data is a Series, convert it to a DataFrame; if it's already a DataFrame, use it as is.
    if isinstance(data, pd.Series):
        df_new = data.to_frame()
    else:
        df_new = data.copy()
    
    # Rename the column to the symbol.
    # If there is more than one column, assume the first one is 'Close'.
    if isinstance(df_new, pd.DataFrame):
        if df_new.shape[1] == 1:
            df_new.columns = [symbol]
        else:
            df_new.rename(columns={df_new.columns[0]: symbol}, inplace=True)
    
    # If the original CSV was empty, use the new data; otherwise, join on the index.
    if df.empty:
        df = df_new
    else:
        df = df.join(df_new, how='outer')
    
    # Optionally, fill NaN values if desired.
    df[symbol] = df[symbol].fillna(method='ffill')
    
    try:
        df.to_csv(csv_file)
    except Exception as e:
        print(f"Error writing CSV file: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Symbol {symbol} added to CSV successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: update_csv.py <csv_file> <symbol>", file=sys.stderr)
        sys.exit(1)
    csv_file = sys.argv[1]
    symbol = sys.argv[2]
    update_csv(csv_file, symbol)
