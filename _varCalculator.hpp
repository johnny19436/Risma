#pragma once
#include <vector>
#include <memory>
#include "_portfolio.hpp"

class VaRCalculator {
public:
    VaRCalculator(double confidence_level = 0.95);
    
    double computeVaR(const Portfolio& portfolio, int num_simulations = 100000);
    double computeES(const Portfolio& portfolio, int num_simulations = 100000);
    std::vector<double> runMonteCarlo(const Portfolio& portfolio, int num_simulations);

private:
    double confidence_level_; 
}; 