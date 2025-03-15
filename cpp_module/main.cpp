#include <iostream>
#include <chrono>
#include "portfolio.hpp"
#include "var_calculator.hpp"

int main() {
    // Create a sample portfolio
    Portfolio portfolio;
    portfolio.addAsset("AAPL", 0.4, 150.0, 0.2);  // 40% Apple stock
    portfolio.addAsset("GOOGL", 0.6, 2800.0, 0.25);  // 60% Google stock

    // Create VaR calculator
    VaRCalculator calculator(0.95);  // 95% confidence level

    // Start timing
    auto start = std::chrono::high_resolution_clock::now();

    // Calculate VaR and ES
    double var = calculator.computeVaR(portfolio);
    double es = calculator.computeES(portfolio);

    // End timing
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::cout << "Portfolio Risk Metrics:" << std::endl;
    std::cout << "Value at Risk (95%): $" << var << std::endl;
    std::cout << "Expected Shortfall (95%): $" << es << std::endl;
    std::cout << "Computation Time: " << duration.count() << " milliseconds" << std::endl;

    return 0;
} 