import pandas as pd
import numpy as np
import yfinance as yf
import _varCalculator



def calculate_var():
    # Example portfolio
    stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    weights = np.array([0.3, 0.3, 0.2, 0.2])
    initial_investment = 100000  # $100,000 portfolio
    
    # Download historical data
    portfolio_data = pd.DataFrame()
    for stock in stocks:
        data = yf.download(stock, start='2022-01-01', end='2024-01-01')['Close']
        portfolio_data[stock] = data
    
    # Calculate portfolio returns
    returns = portfolio_data.pct_change().dropna()
    portfolio_returns = returns.dot(weights)
    
    mean_return = portfolio_returns.mean()
    volatility = portfolio_returns.std()
    
    # Calculate VaR at different confidence levels
    confidence_levels = [0.99, 0.95, 0.90]
    
    print(f"Value at Risk (VaR) Analysis for ${initial_investment:,} Portfolio")
    print("=" * 50)
    
    for confidence in confidence_levels:
        # Use the C++ implementation for VaR calculations
        var = _varCalculator.calculate_var(confidence, mean_return, volatility)
        var_dollar = _varCalculator.calculate_dollar_var(initial_investment, var)
        
        print(f"\nAt {confidence*100}% confidence level:")
        print(f"Daily VaR: ${var_dollar:,.2f}")
        print(f"Daily VaR %: {abs(var)*100:.2f}%")

if __name__ == "__main__":
    calculate_var() 