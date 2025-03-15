#include "var_calculator.hpp"
#include <algorithm>
#include <random>
#include <cmath>

VaRCalculator::VaRCalculator(double confidence_level)
    : confidence_level_(confidence_level) {}

double VaRCalculator::computeVaR(const Portfolio& portfolio, int num_simulations) {
    auto returns = runMonteCarlo(portfolio, num_simulations);
    std::sort(returns.begin(), returns.end());
    
    int var_index = static_cast<int>((1.0 - confidence_level_) * num_simulations);
    return -returns[var_index] * portfolio.getTotalValue();
}

double VaRCalculator::computeES(const Portfolio& portfolio, int num_simulations) {
    std::vector<double> returns = runMonteCarlo(portfolio, num_simulations);
    std::sort(returns.begin(), returns.end());
    
    int var_index = static_cast<int>((1.0 - confidence_level_) * num_simulations);
    double es = 0.0;
    for (int i = 0; i < var_index; ++i) {
        es += returns[i];
    }
    return -(es / var_index) * portfolio.getTotalValue();
}

std::vector<double> VaRCalculator::runMonteCarlo(const Portfolio& portfolio, int num_simulations) {
    std::vector<double> returns(num_simulations);
    std::random_device rd;
    std::mt19937 gen(rd());

    // Assumes asset returns are normally distributed
    // Creates a normal distribution with mean = 0 and standard deviation = 1
    std::normal_distribution<> dist(0.0, 1.0); 

    // Simple implementation for prototype
    for (int i = 0; i < num_simulations; ++i) {
        double portfolio_return = 0.0;
        std::vector<Asset> assets = portfolio.getAssets();
        for (const auto& asset : assets) {
            double z = dist(gen);
            portfolio_return += asset.weight * (z * asset.volatility);
        }
        returns[i] = portfolio_return;
    }
    
    return returns;
} 