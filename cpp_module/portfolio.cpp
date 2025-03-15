#include "portfolio.hpp"

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