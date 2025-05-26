import subprocess

def test_cli_add_and_list_portfolio():
    commands = """
    add_portfolio --name cli_test --datafolder ./data
    list_portfolios
    exit
    """
    result = subprocess.run(["python3", "cli.py", "interactive"],
                            input=commands, text=True, capture_output=True)
    assert "cli_test" in result.stdout

def test_cli_add_asset():
    commands = """
    add_portfolio --name cli_test2 --datafolder ./data
    switch_portfolio --name cli_test2
    add_asset --symbol AAPL --weight 0.5
    list_assets
    exit
    """
    result = subprocess.run(["python3", "cli.py", "interactive"],
                            input=commands, text=True, capture_output=True)
    assert "AAPL" in result.stdout

def test_cli_var_es():
    commands = """
    add_portfolio --name cli_test3 --datafolder ./data
    switch_portfolio --name cli_test3
    add_asset --symbol MSFT --weight 1.0
    compute_var --confidence 0.95 --simulations 10000
    compute_es --confidence 0.95 --simulations 10000
    exit
    """
    result = subprocess.run(["python3", "cli.py", "interactive"],
                            input=commands, text=True, capture_output=True)
    assert "Computed VaR" in result.stdout
    assert "Computed Expected Shortfall" in result.stdout
