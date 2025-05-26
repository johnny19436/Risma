#include "_calculator.h"
#include "_portfolioManager.h"
#include <pybind11/pybind11.h>
#include <boost/math/special_functions/erf.hpp>
#include <algorithm>
#include <random>
#include <cmath>
#include <tbb/parallel_sort.h>
#include <omp.h>

namespace py = pybind11;

// Global PortfolioManager instance used by free functions.
PortfolioManager gPortfolioManager;

Calculator::Calculator(double confidence_level)
    : confidence_level_(confidence_level) {}

double Calculator::getConfidenceLevel() const {
    return confidence_level_;
}

void Calculator::setConfidenceLevel(double confidenceLevel) {
    if (confidenceLevel <= 0.0 || confidenceLevel >= 1.0) {
        throw std::invalid_argument("Confidence level must be between 0 and 1.");
    }
    confidence_level_ = confidenceLevel;
}

double Calculator::computeVaR(const Portfolio& portfolio, int num_simulations) {
    auto returns = runMonteCarlo(portfolio, num_simulations);
    
    // Use parallel sort for large arrays
    if (returns.size() > 10000) {
        #pragma omp parallel
        {
            #pragma omp single
            tbb::parallel_sort(returns.begin(), returns.end());
        }
    } else {
        std::sort(returns.begin(), returns.end());
    }
    
    int var_index = static_cast<int>((1.0 - confidence_level_) * num_simulations);
    return -returns[var_index] * portfolio.getAssetTotalWeight();
}

double Calculator::computeES(const Portfolio& portfolio, int num_simulations) {
    std::vector<double> returns = runMonteCarlo(portfolio, num_simulations);
    
    // Use parallel sort for large arrays
    if (returns.size() > 10000) {
        #pragma omp parallel
        {
            #pragma omp single
            tbb::parallel_sort(returns.begin(), returns.end());
        }
    } else {
        std::sort(returns.begin(), returns.end());
    }
    
    int var_index = static_cast<int>((1.0 - confidence_level_) * num_simulations);
    double es = 0.0;
    
    // Parallel reduction for ES calculation
    #pragma omp parallel reduction(+:es)
    {
        #pragma omp for nowait
        for (int i = 0; i < var_index; ++i) {
            es += returns[i];
        }
    }
    
    return -(es / var_index) * portfolio.getAssetTotalWeight();
}

std::vector<double> Calculator::runMonteCarlo(const Portfolio& portfolio, int num_simulations) {
    std::vector<double> returns(num_simulations);
    auto assets = portfolio.listAssets();
    
    // Get number of available threads
    int num_threads = omp_get_max_threads();
    std::vector<std::mt19937> generators(num_threads);
    
    // Initialize random number generators for each thread
    #pragma omp parallel
    {
        int thread_id = omp_get_thread_num();
        std::random_device rd;
        generators[thread_id].seed(rd());
    }
    
    // Parallel Monte Carlo simulation
    #pragma omp parallel
    {
        int thread_id = omp_get_thread_num();
        // std::normal_distribution<> dist(0.0, 1.0);
        int degrees_of_freedom_ = 4;
        std::student_t_distribution<> dist(degrees_of_freedom_);

        
        #pragma omp for nowait
        for (int i = 0; i < num_simulations; ++i) {
            double portfolio_return = 0.0;
            for (const auto& asset : assets) {
                double z = dist(generators[thread_id]);
                portfolio_return += asset.weight * (z * asset.volatility);
            }
            returns[i] = portfolio_return;
        }
    }
    
    return returns;
}

void bind_calculator(py::module_ &m) {
    m.doc() = "VaR and volatility calculations implemented in C++";
    py::class_<Calculator>(m, "Calculator")
        .def(py::init<double>())
        .def("compute_var", &Calculator::computeVaR)
        .def("compute_es", &Calculator::computeES)
        .def("run_monte_carlo", &Calculator::runMonteCarlo)
        .def("get_confidence_level", &Calculator::getConfidenceLevel)
        .def("set_confidence_level", &Calculator::setConfidenceLevel);
}
