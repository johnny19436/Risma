#!/usr/bin/env python3
"""
run_var_es.py – identical workload to batch_var_es.sh, but entirely in Python
so you can point macOS Instruments (Time Profiler) directly at one process.
"""
# # Run Time Profiler and EXEC into python so PID never changes
# xcrun xctrace record \
#   --template "Time Profiler" \
#   --output profile.trace \
#   --launch -- /bin/bash -c "exec python3 profile_var_es.py"

# open profile.trace

import time
import _package as riskcalc   # <-- your pybind11 C++ extension

PORTFOLIO   = "equal_weight"
DATA_FOLDER = "./data"
CONF_LEVEL  = 0.95
SIMULATIONS = 1_000_000

SYMBOLS = [
    # ---------------- full 200‑ticker list ----------------
    "AAPL","MSFT","AMZN","GOOG","META","TSLA","JPM","V","NVDA","DIS",
    "NFLX","ORCL","INTC","AMD","IBM","CSCO","BA","GE","F","GM",
    "QCOM","TXN","MU","LRCX","ADI","AVGO","TSM","ASML","NXPI","STX",
    "PYPL","SHOP","COIN","TWLO","UBER","LYFT","DASH","ABNB","Z",
    "PINS","SNAP","ETSY","EBAY","BABA","BIDU","JD","PDD","NTES","RBLX",
    "PLTR","CRWD","OKTA","NET","ZS","PANW","SNOW","MDB","DDOG","DOCU",
    "ZM","TEAM","CRM","NOW","WDAY","SAP","ADP","INTU","PAYC","ADBE",
    "MS","GOOGL","WFC","BAC","C","GS","SCHW","T","VZ","TMUS",
    "CMCSA","TEF","NOK","ERIC","SONY","DELL","HPQ","LEN","LOW","HD",
    "COST","WMT","TGT","XOM","CVX","BP","EOG","COP","SLB","HAL",
    "OXY","PSX","VLO","MPC","ALB","MMM","ABT","ABBV","ACN","AEP",
    "AIG","ALL","AMGN","AMP","AMT","AVB","AXP","BIIB","BK","BKNG",
    "BLK","BMY","C","CAT","CB","CCI","CL","CLX","CMG","COF",
    "CVS","DHR","DOW","DUK","EL","EMR","ETN","EXC","FDX","GD",
    "GILD","HON","ICE","IDXX","ILMN","INFY","IP","JNJ","KHC","KMI",
    "KSS","LMT","LULU","MA","MCD","MDT","MET","MHK","MO","MRK",
    "MTB","NEE","NKE","NSC","ORLY","PFE","PG","PM","PGR","PSA",
    "RTX","SBUX","SO","SPG","SPGI","TJX","TRV","TSCO","UNH","UNP",
    "UPS","USB","VRTX","WBA","ZBH","ZBRA","ZION","ALGN","ANET","APH",
    "BEN","BAX","BBY","CARR","CF","CHTR","CMI","CTAS","CTSH","DG",
    "DHI"
]  # 200 entries
# ----------------------------------------------------------

def main() -> None:
    mgr  = riskcalc.PortfolioManager()
    calc = riskcalc.Calculator(CONF_LEVEL)

    mgr.addPortfolio(PORTFOLIO, DATA_FOLDER)
    mgr.switchPortfolio(PORTFOLIO)
    port = mgr.getCurrentPortfolio()

    w = 1.0 / len(SYMBOLS)
    for sym in SYMBOLS:
        port.addAsset(sym, w)

    t0 = time.perf_counter()
    var_val = calc.compute_var(port, SIMULATIONS)
    t1 = time.perf_counter()
    es_val  = calc.compute_es(port, SIMULATIONS)
    t2 = time.perf_counter()

    print(f"VaR (95%, N={SIMULATIONS:_}): {var_val:.6g}  [{t1-t0:.2f}s]")
    print(f"ES  (95%, N={SIMULATIONS:_}): {es_val:.6g}  [{t2-t1:.2f}s]")

if __name__ == "__main__":
    main()
