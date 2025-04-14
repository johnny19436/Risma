import _package as riskcalc
import pytest

def test_portfolio_add_and_switch():
    manager = riskcalc.PortfolioManager()
    manager.addPortfolio("test1", "./data")
    manager.addPortfolio("test2", "./data")
    
    assert "test1" in manager.listPortfolios()
    assert "test2" in manager.listPortfolios()
    
    assert manager.switchPortfolio("test2")
    assert manager.getCurrentPortfolio().getName() == "test2"

def test_portfolio_add_asset():
    manager = riskcalc.PortfolioManager()
    manager.addPortfolio("test_port", "./data")
    manager.switchPortfolio("test_port")
    portfolio = manager.getCurrentPortfolio()
    portfolio.addAsset("AAPL", 0.5)
    
    assets = portfolio.listAssets()
    assert any(asset.symbol == "AAPL" for asset in assets)
    assert any(asset.volatility > 0 for asset in assets)

def test_calculator_var_es():
    manager = riskcalc.PortfolioManager()
    manager.addPortfolio("risk_test", "./data")
    manager.switchPortfolio("risk_test")
    portfolio = manager.getCurrentPortfolio()
    portfolio.addAsset("MSFT", 1.0)

    calc = riskcalc.Calculator(0.95)
    var = calc.compute_var(portfolio, 10000)
    es = calc.compute_es(portfolio, 10000)

    assert var > 0
    assert es > var
