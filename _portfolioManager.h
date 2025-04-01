#pragma once
#include <string>
#include <vector>
#include <unordered_map>
#include <utility>

struct Asset {
    std::string symbol;
    float weight;
    float volatility;
};

class Portfolio {
public:

    Portfolio(const std::string &name, const std::string &dataFolder);

    const std::string& getName() const;
    const std::string& getDataFolder() const;

    void addAsset(const std::string &symbol, float weight);
    void modifyAsset(const std::string &symbol, float weight);
    void delAsset(const std::string &symbol);
    std::vector<Asset> listAssets() const;

    double getAssetTotalWeight() const;
    double getAssetWeightedVolatility() const;
    double getAssetTotalValue() const;

private:
    std::string name_;
    std::string dataFolder_;
    std::unordered_map<std::string, float> assetsWeight_;
    std::unordered_map<std::string, float> assetsVolatility_;
};

class PortfolioManager {
public:
    void addPortfolio(const std::string &name, const std::string &dataFolder);
    void delPortfolio(const std::string &name);
    bool switchPortfolio(const std::string &name);
    std::vector<std::string> listPortfolios() const;

    Portfolio* getCurrentPortfolio();

private:
    std::unordered_map<std::string, Portfolio> portfolios_;
    Portfolio* currentPortfolio_ = nullptr;
};
