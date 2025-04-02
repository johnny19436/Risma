#!/usr/bin/env python3
import argparse
import sys
import shlex

# Import the C++ module built with pybind11.
import _package as riskcalc

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
            for asset in assets:
                print(f"  {asset.symbol}: weight={asset.weight}, volatility={asset.volatility}")
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
        if args.confidence:
            calc.set_confidence_level(args.confidence)
        es_value = calc.compute_es(portfolio, args.simulations)
        print(f"Computed Expected Shortfall (ES): {es_value}")
    except Exception as e:
        print(f"Error computing ES: {e}")

def build_command_parsers():
    commands = {}

    # add_portfolio
    parser = argparse.ArgumentParser(prog="add_portfolio")
    parser.add_argument("--name", required=True)
    parser.add_argument("--datafolder", required=True)
    commands["add_portfolio"] = (parser, add_portfolio)

    # del_portfolio
    parser = argparse.ArgumentParser(prog="del_portfolio")
    parser.add_argument("--name", required=True)
    commands["del_portfolio"] = (parser, del_portfolio)

    # switch_portfolio
    parser = argparse.ArgumentParser(prog="switch_portfolio")
    parser.add_argument("--name", required=True)
    commands["switch_portfolio"] = (parser, switch_portfolio)

    # list_portfolios
    parser = argparse.ArgumentParser(prog="list_portfolios")
    commands["list_portfolios"] = (parser, list_portfolios)

    # add_asset
    parser = argparse.ArgumentParser(prog="add_asset")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--weight", type=float, required=True)
    commands["add_asset"] = (parser, add_asset)

    # modify_asset
    parser = argparse.ArgumentParser(prog="modify_asset")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--weight", type=float, required=True)
    commands["modify_asset"] = (parser, modify_asset)

    # del_asset
    parser = argparse.ArgumentParser(prog="del_asset")
    parser.add_argument("--symbol", required=True)
    commands["del_asset"] = (parser, del_asset)

    # list_assets
    parser = argparse.ArgumentParser(prog="list_assets")
    commands["list_assets"] = (parser, list_assets)

    # compute_var
    parser = argparse.ArgumentParser(prog="compute_var")
    parser.add_argument("--confidence", type=float, default=None)
    parser.add_argument("--simulations", type=int, default=100000)
    commands["compute_var"] = (parser, compute_var)

    # compute_es
    parser = argparse.ArgumentParser(prog="compute_es")
    parser.add_argument("--confidence", type=float, default=None)
    parser.add_argument("--simulations", type=int, default=100000)
    commands["compute_es"] = (parser, compute_es)

    return commands

def interactive():
    print("Entering interactive mode. Type 'help' for commands, 'exit' to quit.")
    commands = build_command_parsers()
    while True:
        try:
            command_line = input(">> ").strip()
            if command_line in ['exit', 'quit']:
                break
            if command_line == "help":
                print("Available commands:")
                for cmd in commands:
                    print("  " + cmd)
                continue
            if not command_line:
                continue
            # Use shlex to split the command preserving quoted strings
            args_list = shlex.split(command_line)
            cmd_name = args_list[0]
            if cmd_name not in commands:
                print("Unknown command. Type 'help' for available commands.")
                continue
            parser, func = commands[cmd_name]
            try:
                parsed_args = parser.parse_args(args_list[1:])
            except SystemExit:
                # argparse raises SystemExit on error; just continue the loop.
                continue
            func(parsed_args)
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Portfolio Manager CLI: Manage portfolios and compute risk metrics."
    )
    subparsers = parser.add_subparsers(title="subcommands", dest="command")
    
    # Non-interactive commands (if desired)
    parser_interactive = subparsers.add_parser("interactive", help="Run in interactive mode")
    parser_interactive.set_defaults(func=lambda args: interactive())

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    main()
