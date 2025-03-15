import numpy as np
import time
from typing import List, Dict

class Portfolio:
    def __init__(self):
        self.assets: Dict[str, Dict] = {}
    
    def add_asset(self, symbol: str, weight: float, price: float, volatility: float):
        self.assets[symbol] = {
            'weight': weight,
            'price': price,
            'volatility': volatility
        }
    
    def get_total_value(self) -> float:
        return sum(asset['weight'] * asset['price'] for asset in self.assets.values())

class RiskCalculator:
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
    
    def compute_var(self, portfolio: Portfolio, num_simulations: int = 100000) -> float:
        returns = self._run_monte_carlo(portfolio, num_simulations)
        var_index = int((1.0 - self.confidence_level) * num_simulations)
        sorted_returns = np.sort(returns)
        return -sorted_returns[var_index] * portfolio.get_total_value()
    
    def compute_es(self, portfolio: Portfolio, num_simulations: int = 100000) -> float:
        returns = self._run_monte_carlo(portfolio, num_simulations)
        var_index = int((1.0 - self.confidence_level) * num_simulations)
        sorted_returns = np.sort(returns)
        es = np.mean(sorted_returns[:var_index])
        return -es * portfolio.get_total_value()
    
    def _run_monte_carlo(self, portfolio: Portfolio, num_simulations: int) -> np.ndarray:
        returns = np.zeros(num_simulations)
        for symbol, asset in portfolio.assets.items():
            z = np.random.normal(0, 1, num_simulations)
            returns += asset['weight'] * (z * asset['volatility'])
        return returns

def main():
    # Create a sample portfolio
    portfolio = Portfolio()
    portfolio.add_asset("AAPL", 0.4, 150.0, 0.2)  # 40% Apple stock
    portfolio.add_asset("GOOGL", 0.6, 2800.0, 0.25)  # 60% Google stock

    # Create risk calculator
    calculator = RiskCalculator(confidence_level=0.95)

    # Start timing
    start_time = time.time()

    # Calculate VaR and ES
    var = calculator.compute_var(portfolio)
    es = calculator.compute_es(portfolio)

    # End timing
    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000  # Convert to milliseconds

    print("Portfolio Risk Metrics:")
    print(f"Value at Risk (95%): ${var:.2f}")
    print(f"Expected Shortfall (95%): ${es:.2f}")
    print(f"Computation Time: {duration_ms:.2f} milliseconds")

if __name__ == "__main__":
    main() 