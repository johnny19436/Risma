import click
import numpy as np
import _package
import pandas as pd

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1.0')
def cli():
    """Risma: A Risk Management Tool for Portfolio Analysis

    This tool provides risk metrics calculation for financial portfolios.

    Commands:
    \b
    var       Calculate VaR and ES for a series of returns
    portfolio Analyze risk metrics for a portfolio from CSV
    
    Examples:
    \b
    # Calculate VaR for a series of returns
    risma var -c 0.95 0.01 -0.02 0.015
    
    # Analyze portfolio from CSV file
    risma portfolio -f data.csv -c 0.99
    """
    pass

@cli.command(help='Calculate VaR and ES for a series of returns')
@click.option('--confidence', '-c', 
              default=0.95, 
              type=click.FloatRange(0, 1, min_open=True, max_open=True),
              help='Confidence level (0-1, default: 0.95)')
@click.argument('returns', nargs=-1, type=float)
def var(confidence, returns):
    """Calculate Value at Risk (VaR) and Expected Shortfall (ES).

    RETURNS: Space-separated list of return values
    
    Example:
    \b
    risma var -c 0.95 -- 0.01 -0.02 0.015 0.02 -0.01
    """
    if not returns:
        click.echo('Error: Please provide return values')
        return

    try:
        # Import Portfolio and VaRCalculator from your package
        from _package import Portfolio, VaRCalculator
        
        # Create a portfolio and a VaRCalculator instance
        portfolio = Portfolio()
        calculator = VaRCalculator(confidence)
        
        # Convert the list of returns to a NumPy array and add as an asset.
        # (Adjust the add_asset method parameters if needed.)
        returns_array = np.array(returns)
        portfolio.add_asset("Asset1", returns_array)
        
        # Use the calculator object to compute risk metrics
        var_result = calculator.calculate_var(portfolio, confidence)
        es_result = calculator.calculate_es(portfolio, confidence)
        
        click.echo("\nRisk Metrics:")
        click.echo("─" * 40)
        click.echo(f"Number of observations: {len(returns)}")
        click.echo(f"Confidence level: {confidence:.1%}")
        click.echo(f"Value at Risk (VaR): {var_result:.4f}")
        click.echo(f"Expected Shortfall (ES): {es_result:.4f}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}")

@cli.command(help='Analyze portfolio risk metrics from a CSV file')
@click.option('--file', '-f', 
              required=True, 
              type=click.Path(exists=True, dir_okay=False, resolve_path=True),
              help='Path to CSV file containing returns data')
@click.option('--confidence', '-c', 
              default=0.95, 
              type=click.FloatRange(0, 1, min_open=True, max_open=True),
              help='Confidence level (0-1, default: 0.95)')
def portfolio(file, confidence):
    """Analyze portfolio risk metrics from a CSV file.

    The CSV file should have:
    \b
    - Assets as columns
    - Returns as rows
    - Optional 'Date' column (will be ignored)
    
    Example:
    \b
    risma portfolio -f data.csv -c 0.95
    """
    try:
        # Read CSV data into a DataFrame
        df = pd.read_csv(file)
        
        # Import Portfolio and VaRCalculator from your package
        from _package import Portfolio, VaRCalculator
        
        # Create a portfolio and a VaRCalculator instance
        portfolio = Portfolio()
        calculator = VaRCalculator()
        
        # Add each column as an asset (ignoring a 'Date' column if present)
        asset_count = 0
        for column in df.columns:
            if column.lower() != 'date':
                portfolio.add_asset(column, df[column].values)
                asset_count += 1
        
        # Compute VaR and ES using the calculator
        var_result = calculator.calculate_var(portfolio, confidence)
        es_result = calculator.calculate_es(portfolio, confidence)
        
        click.echo("\nPortfolio Risk Analysis:")
        click.echo("─" * 40)
        click.echo(f"Number of assets: {asset_count}")
        click.echo(f"Observations per asset: {len(df)}")
        click.echo(f"Confidence level: {confidence:.1%}")
        click.echo(f"Portfolio VaR: {var_result:.4f}")
        click.echo(f"Portfolio ES: {es_result:.4f}")
    
    except Exception as e:
        click.echo(f"Error: {str(e)}")

def main():
    """Entry point for the CLI."""
    cli(prog_name='risma')

if __name__ == '__main__':
    main()
