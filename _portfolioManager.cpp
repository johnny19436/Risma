#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <fstream>
#include <sstream>
#include <filesystem>
#include "_portfolioManager.h"

namespace fs = std::filesystem;
namespace py = pybind11;
// ----------------------- Portfolio Implementation -----------------------

Portfolio::Portfolio(const std::string &name, const std::string &dataFolder)
    : name_(name), dataFolder_(dataFolder) {}

const std::string& Portfolio::getName() const {
    return name_;
}

const std::string& Portfolio::getDataFolder() const {
    return dataFolder_;
}

void Portfolio::addAsset(const std::string &symbol, float weight) {
    // Insert or update asset weight
    assetsWeight_[symbol] = weight;

    // Construct file path (assumes CSV file named "prices.csv" in dataFolder_)
    std::string filename = dataFolder_ + "/prices.csv";
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Unable to open file: " + filename);
    }

    std::string line;
    // Read the header line to get column names; if empty, call update_csv
    if (!std::getline(file, line) || line.empty()) {
        file.close();
        // File is empty: call external Python script to create data for this symbol.
        std::string command = "python update_csv.py \"" + filename + "\" " + symbol;
        int ret = std::system(command.c_str());
        if (ret != 0) {
            throw std::runtime_error("Failed to update CSV for symbol: " + symbol);
        }
        // Re-open the file after update.
        file.open(filename);
        if (!file.is_open() || !std::getline(file, line) || line.empty()) {
            throw std::runtime_error("File is still empty after update: " + filename);
        }
    }

    std::istringstream headerStream(line);
    std::vector<std::string> headers;
    std::string header;
    while (std::getline(headerStream, header, ',')) {
        headers.push_back(header);
    }

    // Check if the symbol exists in the CSV header.
    int symbolIndex = -1;
    for (int i = 0; i < static_cast<int>(headers.size()); ++i) {
        if (headers[i] == symbol) {
            symbolIndex = i;
            break;
        }
    }
    
    // If the symbol is not found, update the CSV file by calling an external Python script.
    if (symbolIndex == -1) {
        std::string command = "python update_csv.py \"" + filename + "\" " + symbol;
        int ret = std::system(command.c_str());
        if (ret != 0) {
            throw std::runtime_error("Failed to update CSV for symbol: " + symbol);
        }
        // Re-open the file to refresh the header.
        file.close();
        file.open(filename);
        if (!file.is_open() || !std::getline(file, line)) {
            throw std::runtime_error("Unable to re-read file after update: " + filename);
        }
        headerStream.clear();
        headerStream.str(line);
        headers.clear();
        while (std::getline(headerStream, header, ',')) {
            headers.push_back(header);
        }
        // Find the index again.
        for (int i = 0; i < static_cast<int>(headers.size()); ++i) {
            if (headers[i] == symbol) {
                symbolIndex = i;
                break;
            }
        }
        if (symbolIndex == -1) {
            throw std::runtime_error("Symbol still not found in data file after update: " + symbol);
        }
    }

    // Read price data for the given symbol
    std::vector<double> prices;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        std::istringstream lineStream(line);
        std::string cell;
        int col = 0;
        bool found = false;
        double price = 0.0;
        while (std::getline(lineStream, cell, ',')) {
            if (col == symbolIndex) {
                try {
                    price = std::stod(cell);
                    found = true;
                } catch (const std::exception&) {
                    found = false;
                }
                break;
            }
            ++col;
        }
        if (found) {
            prices.push_back(price);
        }
    }
    file.close();

    if (prices.size() < 2) {
        throw std::runtime_error("Not enough data to compute volatility for symbol: " + symbol);
    }

    // Compute daily returns: (price[t] - price[t-1]) / price[t-1]
    std::vector<double> returns;
    for (size_t i = 1; i < prices.size(); ++i) {
        double dailyReturn = (prices[i] - prices[i - 1]) / prices[i - 1];
        returns.push_back(dailyReturn);
    }

    // Calculate mean of returns
    double sum = 0.0;
    for (double r : returns) {
        sum += r;
    }
    double mean = sum / returns.size();

    // Calculate sample standard deviation (volatility)
    double variance = 0.0;
    for (double r : returns) {
        variance += (r - mean) * (r - mean);
    }
    variance /= (returns.size() - 1);
    double vol = std::sqrt(variance);

    // Update asset volatility with computed value
    assetsVolatility_[symbol] = static_cast<float>(vol);
}


void Portfolio::modifyAsset(const std::string &symbol, float weight) {
    // Only modify if the asset exists
    if (assetsWeight_.find(symbol) != assetsWeight_.end()) {
        assetsWeight_[symbol] = weight;
    } else {
        throw std::runtime_error("Asset not found: " + symbol);
    }
}

void Portfolio::delAsset(const std::string &symbol) {
    // Erase asset from in-memory maps.
    assetsWeight_.erase(symbol);
    assetsVolatility_.erase(symbol);

    // Construct file path for the CSV file.
    std::string filename = dataFolder_ + "/prices.csv";
    fs::path filePath(filename);
    
    if (!fs::exists(filePath)) {
        // If file doesn't exist, nothing more to do.
        return;
    }
    
    // Read the entire CSV file.
    std::ifstream infile(filename);
    if (!infile.is_open()) {
        throw std::runtime_error("Unable to open file for reading: " + filename);
    }
    
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(infile, line)) {
        lines.push_back(line);
    }
    infile.close();

    if (lines.empty()) {
        // Nothing to update if file is empty.
        return;
    }

    // Process the header to determine the index of the column to remove.
    std::istringstream headerStream(lines[0]);
    std::string token;
    std::vector<std::string> headers;
    while (std::getline(headerStream, token, ',')) {
        headers.push_back(token);
    }
    
    // Find index of the asset's column.
    int colIndex = -1;
    for (size_t i = 0; i < headers.size(); ++i) {
        if (headers[i] == symbol) {
            colIndex = static_cast<int>(i);
            break;
        }
    }
    if (colIndex == -1) {
        // Asset column not found in file, so nothing to remove.
        return;
    }
    
    // Remove the asset's header.
    headers.erase(headers.begin() + colIndex);
    
    // Prepare a vector to hold updated lines.
    std::vector<std::string> updatedLines;
    
    // Rebuild header line.
    std::ostringstream newHeader;
    for (size_t i = 0; i < headers.size(); ++i) {
        newHeader << headers[i];
        if (i != headers.size() - 1) {
            newHeader << ",";
        }
    }
    updatedLines.push_back(newHeader.str());
    
    // Process each subsequent line: remove the cell at colIndex.
    for (size_t i = 1; i < lines.size(); ++i) {
        std::istringstream lineStream(lines[i]);
        std::string cell;
        std::vector<std::string> cells;
        while (std::getline(lineStream, cell, ',')) {
            cells.push_back(cell);
        }
        // If the number of cells matches header count+1, remove the unwanted cell.
        if (cells.size() > static_cast<size_t>(colIndex)) {
            cells.erase(cells.begin() + colIndex);
        }
        // Rebuild the line.
        std::ostringstream newLine;
        for (size_t j = 0; j < cells.size(); ++j) {
            newLine << cells[j];
            if (j != cells.size() - 1) {
                newLine << ",";
            }
        }
        updatedLines.push_back(newLine.str());
    }
    
    // Write the updated CSV back to the file.
    std::ofstream outfile(filename, std::ios::trunc);
    if (!outfile.is_open()) {
        throw std::runtime_error("Unable to open file for writing: " + filename);
    }
    for (const auto &l : updatedLines) {
        outfile << l << "\n";
    }
    outfile.close();
}

std::vector<Asset> Portfolio::listAssets() const {
    std::vector<Asset> assetList;
    for (const auto &entry : assetsWeight_) {
        Asset asset;
        asset.symbol = entry.first;
        asset.weight = entry.second;
        // Retrieve volatility; if not found, default to 0.0.
        auto it = assetsVolatility_.find(entry.first);
        asset.volatility = (it != assetsVolatility_.end()) ? it->second : 0.0f;
        assetList.push_back(asset);
    }
    return assetList;
}

double Portfolio::getAssetTotalWeight() const {
    double totalWeight = 0.0;
    for (const auto &entry : assetsWeight_) {
        totalWeight += entry.second;
    }
    return totalWeight;
}

double Portfolio::getAssetWeightedVolatility() const {
    double weightedVolatility = 0.0;
    for (const auto &entry : assetsWeight_) {
        const std::string &symbol = entry.first;
        double weight = entry.second;
        double volatility = assetsVolatility_.at(symbol);
        weightedVolatility += weight * volatility;
    }
    return weightedVolatility;
}

double Portfolio::getAssetTotalValue() const {
    double totalValue = 0.0;
    for (const auto &entry : assetsWeight_) {
        const std::string &symbol = entry.first;
        double weight = entry.second;
        double price = 0.0; // Placeholder for actual price retrieval
        totalValue += weight * price;
    }
    return totalValue;
}


// ----------------------- PortfolioManager Implementation -----------------------

void PortfolioManager::addPortfolio(const std::string &name, const std::string &dataFolder) {
    // Create the directory if it doesn't exist.
    fs::path dir(dataFolder);
    if (!fs::exists(dir)) {
        if (!fs::create_directories(dir)) {
            throw std::runtime_error("Failed to create directory: " + dataFolder);
        }
    }

    // Insert a new portfolio into the map.
    portfolios_.emplace(name, Portfolio(name, dataFolder));

    // Optionally, set as current portfolio if none is active.
    if (!currentPortfolio_) {
        currentPortfolio_ = &portfolios_.at(name);
    }
}

void PortfolioManager::delPortfolio(const std::string &name) {
    // Find the portfolio in the map.
    auto it = portfolios_.find(name);
    if (it != portfolios_.end()) {
        // Remove the associated data folder if it exists.
        fs::path dir(it->second.getDataFolder());
        if (fs::exists(dir)) {
            fs::remove_all(dir);  // Deletes the directory and all its contents.
        }
        
        // If the portfolio to be deleted is currently active, reset currentPortfolio_
        if (currentPortfolio_ == &(it->second)) {
            currentPortfolio_ = nullptr;
        }
        portfolios_.erase(it);
    } else {
        throw std::runtime_error("Portfolio not found: " + name);
    }
}

bool PortfolioManager::switchPortfolio(const std::string &name) {
    // Set currentPortfolio_ if the portfolio exists.
    auto it = portfolios_.find(name);
    if (it != portfolios_.end()) {
        currentPortfolio_ = &(it->second);
        return true;
    }
    return false;
}

std::vector<std::string> PortfolioManager::listPortfolios() const {
    std::vector<std::string> names;
    for (const auto &entry : portfolios_) {
        names.push_back(entry.first);
    }
    return names;
}

Portfolio* PortfolioManager::getCurrentPortfolio() {
    return currentPortfolio_;
}

void bind_portfolio(py::module_ &m) {
    m.doc() = "Portfolio Manager module";

    // Bind the Asset struct.
    py::class_<Asset>(m, "Asset")
        .def_readonly("symbol", &Asset::symbol)
        .def_readonly("weight", &Asset::weight)
        .def_readonly("volatility", &Asset::volatility);

    // Bind the Portfolio class.
    py::class_<Portfolio>(m, "Portfolio")
        .def(py::init<const std::string &, const std::string &>(),
             py::arg("name"), py::arg("data_folder"))
        .def("getName", &Portfolio::getName, "Get the portfolio name")
        .def("getDataFolder", &Portfolio::getDataFolder, "Get the portfolio data folder")
        .def("addAsset", &Portfolio::addAsset, py::arg("symbol"), py::arg("weight"),
             "Add an asset (updates weight and computes volatility)")
        .def("modifyAsset", &Portfolio::modifyAsset, py::arg("symbol"), py::arg("weight"),
             "Modify an existing asset's weight")
        .def("delAsset", &Portfolio::delAsset, py::arg("symbol"),
             "Delete an asset")
        .def("listAssets", &Portfolio::listAssets,
             "List all assets as Asset structs")
        .def("getAssetTotalWeight", &Portfolio::getAssetTotalWeight,
             "Get the total weight of all assets")
        .def("getAssetWeightedVolatility", &Portfolio::getAssetWeightedVolatility,
             "Get the weighted volatility of the assets")
        .def("getAssetTotalValue", &Portfolio::getAssetTotalValue,
             "Get the total value of the assets");

    // Bind the PortfolioManager class.
    py::class_<PortfolioManager>(m, "PortfolioManager")
        .def(py::init<>())
        .def("addPortfolio", &PortfolioManager::addPortfolio, py::arg("name"), py::arg("data_folder"),
             "Add a new portfolio")
        .def("delPortfolio", &PortfolioManager::delPortfolio, py::arg("name"),
             "Delete an existing portfolio")
        .def("switchPortfolio", &PortfolioManager::switchPortfolio, py::arg("name"),
             "Switch the active portfolio")
        .def("listPortfolios", &PortfolioManager::listPortfolios,
             "List all portfolio names")
        .def("getCurrentPortfolio", &PortfolioManager::getCurrentPortfolio,
             py::return_value_policy::reference,
             "Get the currently active portfolio (or None if not set)");
}