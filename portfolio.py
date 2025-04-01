import _varCalculator
import pandas as pd
import numpy as np
import yfinance as yf


def create_portfolio():
    # Example portfolio with some tech stocks
    stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    weights = np.array([0.3, 0.3, 0.2, 0.2])  # Portfolio weights
    
    # Download historical data
    portfolio_data = pd.DataFrame()
    for stock in stocks:
        data = yf.download(stock, start='2022-01-01', end='2024-01-01')['Close']
        portfolio_data[stock] = data
    
    # Calculate portfolio returns
    returns = portfolio_data.pct_change().dropna()
    
    # Use the C++ implementation for calculations
    portfolio_return = _varCalculator.calculate_portfolio_return(returns.values, weights)
    portfolio_volatility = _varCalculator.calculate_portfolio_volatility(returns.values, weights)
    
    print("Portfolio Composition:")
    for stock, weight in zip(stocks, weights):
        print(f"{stock}: {weight*100}%")
    
    print("\nPortfolio Statistics:")
    print(f"Average Daily Return: {portfolio_return*100:.2f}%")
    print(f"Daily Volatility: {portfolio_volatility*100:.2f}%")
    print(f"Annual Volatility: {portfolio_volatility*np.sqrt(252)*100:.2f}%")

if __name__ == "__main__":
    create_portfolio() 