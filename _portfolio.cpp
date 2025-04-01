#include "_portfolio.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>

namespace py = pybind11;

void Portfolio::addAsset(const std::string& symbol, double weight, double price, double volatility) {
    assets_.push_back({symbol, weight, price, volatility});
}

std::vector<Asset> Portfolio::getAssets() const {
    return assets_;
}

double Portfolio::getTotalValue() const {
    double total = 0.0;
    for (const auto& asset : assets_) {
        total += asset.price * asset.weight;
    }
    return total;
}

double calculate_portfolio_return(py::array_t<double> returns, py::array_t<double> weights) {
    auto r_buf = returns.unchecked<2>();  // 2D array for returns matrix
    auto w_buf = weights.unchecked<1>();  // 1D array for weights
    
    double portfolio_return = 0.0;
    for (py::ssize_t i = 0; i < r_buf.shape(1); i++) {  // iterate over stocks
        double stock_return = 0.0;
        for (py::ssize_t j = 0; j < r_buf.shape(0); j++) {  // iterate over time periods
            stock_return += r_buf(j, i);
        }
        stock_return /= r_buf.shape(0);  // average return for this stock
        portfolio_return += stock_return * w_buf(i);
    }
    return portfolio_return;
}

double calculate_portfolio_volatility(py::array_t<double> returns, py::array_t<double> weights) {
    auto r_buf = returns.unchecked<2>();
    auto w_buf = weights.unchecked<1>();
    
    // Calculate weighted returns for each time period
    std::vector<double> weighted_returns(r_buf.shape(0), 0.0);
    for (py::ssize_t i = 0; i < r_buf.shape(0); i++) {
        for (py::ssize_t j = 0; j < r_buf.shape(1); j++) {
            weighted_returns[i] += r_buf(i, j) * w_buf(j);
        }
    }
    
    // Calculate mean
    double mean = 0.0;
    for (const double& r : weighted_returns) {
        mean += r;
    }
    mean /= weighted_returns.size();
    
    // Calculate variance
    double variance = 0.0;
    for (const double& r : weighted_returns) {
        double diff = r - mean;
        variance += diff * diff;
    }
    variance /= (weighted_returns.size() - 1);
    
    return std::sqrt(variance);
}

PYBIND11_MODULE(_portfolio, m) {
    m.doc() = "Portfolio calculations implemented in C++";
    m.def("calculate_portfolio_return", &calculate_portfolio_return, "Calculate portfolio return");
    m.def("calculate_portfolio_volatility", &calculate_portfolio_volatility, "Calculate portfolio volatility");
    /// Portfolio class
    py::class_<Portfolio>(m, "Portfolio")
        .def(py::init<>())
        .def("add_asset", &Portfolio::addAsset)
        .def("get_assets", &Portfolio::getAssets)
        .def("get_total_value", &Portfolio::getTotalValue);
    /// Asset struct
    py::class_<Asset>(m, "Asset")
        .def_readonly("symbol", &Asset::symbol)
        .def_readonly("weight", &Asset::weight)
        .def_readonly("price", &Asset::price)
        .def_readonly("volatility", &Asset::volatility);
}