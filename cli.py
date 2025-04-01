#!/usr/bin/env python3
import argparse
import sys

# Import the C++ module built with pybind11.
# Adjust the module name if needed.
import _package as riskcalc

# Create a global PortfolioManager and Calculator instance.
# The Calculator is initialized with a default confidence level (0.95).

# To add a portfolio:
# python cli.py add_portfolio --name MyPortfolio --datafolder ./data

# To switch to a portfolio:
# python cli.py switch_portfolio --name MyPortfolio

# To add an asset:
# python cli.py add_asset --symbol AAPL --weight 0.15

# To compute VaR with a 95% confidence level:
# python cli.py compute_var --confidence 0.95


manager = riskcalc.PortfolioManager()
calc = riskcalc.Calculator(0.95)

def add_portfolio(args):
    try:
        manager.addPortfolio(args.name, args.datafolder)
        print(f"Portfolio '{args.name}' added with data folder '{args.datafolder}'.")
    except Exception as e:
        print(f"Error adding portfolio: {e}")

def del_portfolio(args):
    try:
        manager.delPortfolio(args.name)
        print(f"Portfolio '{args.name}' deleted.")
    except Exception as e:
        print(f"Error deleting portfolio: {e}")

def switch_portfolio(args):
    try:
        if manager.switchPortfolio(args.name):
            print(f"Switched to portfolio '{args.name}'.")
        else:
            print(f"Portfolio '{args.name}' not found.")
    except Exception as e:
        print(f"Error switching portfolio: {e}")

def list_portfolios(args):
    try:
        portfolios = manager.listPortfolios()
        if portfolios:
            print("Portfolios:")
            for name in portfolios:
                print(f"  {name}")
        else:
            print("No portfolios available.")
    except Exception as e:
        print(f"Error listing portfolios: {e}")

def add_asset(args):
    try:
        portfolio = manager.getCurrentPortfolio()
        if portfolio is None:
            print("No active portfolio. Please switch to a portfolio first.")
            return
        portfolio.addAsset(args.symbol, args.weight)
        print(f"Asset '{args.symbol}' added/updated with weight {args.weight} in portfolio '{portfolio.getName()}'.")
    except Exception as e:
        print(f"Error adding asset: {e}")

def modify_asset(args):
    try:
        portfolio = manager.getCurrentPortfolio()
        if portfolio is None:
            print("No active portfolio. Please switch to a portfolio first.")
            return
        portfolio.modifyAsset(args.symbol, args.weight)
        print(f"Asset '{args.symbol}' modified to weight {args.weight} in portfolio '{portfolio.getName()}'.")
    except Exception as e:
        print(f"Error modifying asset: {e}")

def del_asset(args):
    try:
        portfolio = manager.getCurrentPortfolio()
        if portfolio is None:
            print("No active portfolio. Please switch to a portfolio first.")
            return
        portfolio.delAsset(args.symbol)
        print(f"Asset '{args.symbol}' deleted from portfolio '{portfolio.getName()}'.")
    except Exception as e:
        print(f"Error deleting asset: {e}")

def list_assets(args):
    try:
        portfolio = manager.getCurrentPortfolio()
        if portfolio is None:
            print("No active portfolio. Please switch to a portfolio first.")
            return
        assets = portfolio.listAssets()
        if assets:
            print(f"Assets in portfolio '{portfolio.getName()}':")
            for symbol, weight in assets:
                print(f"  {symbol}: weight={weight}")
        else:
            print(f"No assets in portfolio '{portfolio.getName()}'.")
    except Exception as e:
        print(f"Error listing assets: {e}")

def compute_var(args):
    try:
        portfolio = manager.getCurrentPortfolio()
        if portfolio is None:
            print("No active portfolio. Please switch to a portfolio first.")
            return
        # Set confidence level if provided
        if args.confidence:
            calc.set_confidence_level(args.confidence)
        var_value = calc.compute_var(portfolio, args.simulations)
        print(f"Computed VaR: {var_value}")
    except Exception as e:
        print(f"Error computing VaR: {e}")

def compute_es(args):
    try:
        portfolio = manager.getCurrentPortfolio()
        if portfolio is None:
            print("No active portfolio. Please switch to a portfolio first.")
            return
        # Set confidence level if provided
        if args.confidence:
            calc.set_confidence_level(args.confidence)
        es_value = calc.compute_es(portfolio, args.simulations)
        print(f"Computed Expected Shortfall (ES): {es_value}")
    except Exception as e:
        print(f"Error computing ES: {e}")

def compute_volatility(args):
    try:
        # Compute volatility for the given symbol using the Calculator's function.
        vol = calc.computeVolatility(args.symbol)
        print(f"Volatility for asset '{args.symbol}': {vol}")
    except Exception as e:
        print(f"Error computing volatility: {e}")

def interactive():
    print("Entering interactive mode. Type 'help' for commands, 'exit' to quit.")
    while True:
        try:
            command = input(">> ").strip()
            if command in ['exit', 'quit']:
                break
            elif command == 'help':
                print("Available commands:")
                print("  add_portfolio --name NAME --datafolder PATH")
                print("  switch_portfolio --name NAME")
                print("  add_asset --symbol SYMBOL --weight WEIGHT")
                print("  list_portfolios")
                print("  list_assets")
                print("  compute_var --confidence CONF --simulations N")
                continue
            # Parse the input into arguments using split (a more robust solution would use shlex)
            args = command.split()
            if not args:
                continue
            subcommand = args[0]
            if subcommand == "add_portfolio":
                parser = argparse.ArgumentParser(prog="add_portfolio")
                parser.add_argument("--name", required=True)
                parser.add_argument("--datafolder", required=True)
                parsed = parser.parse_args(args[1:])
                add_portfolio(parsed)
            elif subcommand == "switch_portfolio":
                parser = argparse.ArgumentParser(prog="switch_portfolio")
                parser.add_argument("--name", required=True)
                parsed = parser.parse_args(args[1:])
                switch_portfolio(parsed)
            # Add additional commands here similarly...
            else:
                print("Unknown command. Type 'help' for available commands.")
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Portfolio Manager CLI: Manage portfolios and compute risk metrics."
    )
    subparsers = parser.add_subparsers(title="subcommands", dest="command")
    
    # add_portfolio
    parser_add_portfolio = subparsers.add_parser("add_portfolio", help="Add a new portfolio")
    parser_add_portfolio.add_argument("--name", required=True, help="Portfolio name")
    parser_add_portfolio.add_argument("--datafolder", required=True, help="Data folder for portfolio")
    parser_add_portfolio.set_defaults(func=add_portfolio)

    # del_portfolio
    parser_del_portfolio = subparsers.add_parser("del_portfolio", help="Delete a portfolio")
    parser_del_portfolio.add_argument("--name", required=True, help="Portfolio name")
    parser_del_portfolio.set_defaults(func=del_portfolio)

    # switch_portfolio
    parser_switch_portfolio = subparsers.add_parser("switch_portfolio", help="Switch active portfolio")
    parser_switch_portfolio.add_argument("--name", required=True, help="Portfolio name")
    parser_switch_portfolio.set_defaults(func=switch_portfolio)

    # list_portfolios
    parser_list_portfolios = subparsers.add_parser("list_portfolios", help="List all portfolios")
    parser_list_portfolios.set_defaults(func=list_portfolios)

    # add_asset
    parser_add_asset = subparsers.add_parser("add_asset", help="Add asset to active portfolio")
    parser_add_asset.add_argument("--symbol", required=True, help="Asset symbol")
    parser_add_asset.add_argument("--weight", type=float, required=True, help="Asset weight")
    parser_add_asset.set_defaults(func=add_asset)

    # modify_asset
    parser_modify_asset = subparsers.add_parser("modify_asset", help="Modify asset weight in active portfolio")
    parser_modify_asset.add_argument("--symbol", required=True, help="Asset symbol")
    parser_modify_asset.add_argument("--weight", type=float, required=True, help="New asset weight")
    parser_modify_asset.set_defaults(func=modify_asset)

    # del_asset
    parser_del_asset = subparsers.add_parser("del_asset", help="Delete asset from active portfolio")
    parser_del_asset.add_argument("--symbol", required=True, help="Asset symbol")
    parser_del_asset.set_defaults(func=del_asset)

    # list_assets
    parser_list_assets = subparsers.add_parser("list_assets", help="List assets in active portfolio")
    parser_list_assets.set_defaults(func=list_assets)

    # compute_var
    parser_compute_var = subparsers.add_parser("compute_var", help="Compute portfolio VaR")
    parser_compute_var.add_argument("--confidence", type=float, help="Confidence level (e.g., 0.95)")
    parser_compute_var.add_argument("--simulations", type=int, default=100000, help="Number of Monte Carlo simulations")
    parser_compute_var.set_defaults(func=compute_var)

    # compute_es
    parser_compute_es = subparsers.add_parser("compute_es", help="Compute portfolio Expected Shortfall (ES)")
    parser_compute_es.add_argument("--confidence", type=float, help="Confidence level (e.g., 0.95)")
    parser_compute_es.add_argument("--simulations", type=int, default=100000, help="Number of Monte Carlo simulations")
    parser_compute_es.set_defaults(func=compute_es)

    # compute_volatility
    parser_compute_vol = subparsers.add_parser("compute_volatility", help="Compute volatility for an asset in active portfolio")
    parser_compute_vol.add_argument("--symbol", required=True, help="Asset symbol")
    parser_compute_vol.set_defaults(func=compute_volatility)

    parser_interactive = subparsers.add_parser("interactive", help="Run in interactive mode")
    parser_interactive.set_defaults(func=lambda args: interactive())

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    main()
