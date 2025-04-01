#pragma once
#include <vector>
#include <memory>
#include "_portfolioManager.h"

class Calculator {
public:
    Calculator(double confidence_level = 0.95);
    double getConfidenceLevel() const;
    void setConfidenceLevel(double confidenceLevel);
    
    double computeVaR(const Portfolio& portfolio, int num_simulations = 100000);
    double computeES(const Portfolio& portfolio, int num_simulations = 100000);
    
    std::vector<double> runMonteCarlo(const Portfolio& portfolio, int num_simulations);

private:
    double confidence_level_; 
}; 
