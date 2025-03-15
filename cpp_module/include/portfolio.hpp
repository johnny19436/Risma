#pragma once
#include <string>
#include <vector>
#include <unordered_map>

struct Asset {
    std::string symbol;
    double weight;
    double price;
    double volatility;
};

class Portfolio {
public:
    void addAsset(const std::string& symbol, double weight, double price, double volatility);
    std::vector<Asset> getAssets() const;
    double getTotalValue() const;

private:
    std::vector<Asset> assets_;
}; 