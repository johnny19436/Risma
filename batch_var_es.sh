#!/usr/bin/env bash
set -euo pipefail

CLI="python3 ./cli.py"
PORTFOLIO="equal_weight"
DATA_FOLDER="./data"
SIMS=3000000
CONF=0.95
DATE_CMD=gdate  # use gdate on macOS; on Linux, use: DATE_CMD=date

SYMBOLS=(AAPL MSFT AMZN GOOG META TSLA JPM V NVDA DIS NFLX ORCL INTC AMD IBM CSCO BA GE F GM
         QCOM TXN MU LRCX ADI AVGO TSM ASML NXPI STX PYPL SHOP COIN TWLO UBER LYFT DASH ABNB Z
         PINS SNAP ETSY EBAY BABA BIDU JD PDD NTES RBLX PLTR CRWD OKTA NET ZS PANW SNOW MDB DDOG
         DOCU ZM TEAM CRM NOW WDAY SAP ADP INTU PAYC ADBE MS GOOGL WFC BAC C GS
         SCHW T VZ TMUS CMCSA TEF NOK ERIC SONY DELL HPQ LEN LOW HD COST WMT TGT
         XOM CVX BP EOG COP SLB HAL OXY PSX VLO MPC ALB)

MORE_SYMBOLS=(
  MMM ABT ABBV ACN AEP AIG ALL AMGN AMP AMT AVB AXP
  BIIB BK BKNG BLK BMY C CAT CB CCI CL CLX CMG COF CVS
  DHR DOW DUK EL EMR ETN EXC FDX GD GILD HON ICE IDXX ILMN
  INFY IP JNJ KHC KMI KSS LMT LULU MA MCD MDT MET MHK MO
  MRK MTB NEE NKE NSC ORLY PFE PG PM PGR PSA RTX SBUX
  SO SPG SPGI TJX TRV TSCO UNH UNP UPS USB VRTX WBA
  ZBH ZBRA ZION ALGN ANET APH BEN BAX BBY CARR CF
  CHTR CMI CTAS CTSH DG DHI
)

# append them
SYMBOLS+=( "${MORE_SYMBOLS[@]}" )

WEIGHT=$(awk -v n="${#SYMBOLS[@]}" 'BEGIN { printf("%.6f", 1/n) }')
TMPFILE=$(mktemp)
trap "rm -f $TMPFILE" EXIT

# First update the CSV file with all symbols
echo "==> Updating price data..."
python3 - "$DATA_FOLDER/prices.csv" "${SYMBOLS[@]}" << 'EOF'
import sys
import update_csv
csv_file = sys.argv[1]
symbols = sys.argv[2:]
success = update_csv.update_csv_bulk(csv_file, symbols)
sys.exit(0 if success else 1)
EOF

# Then build and run the portfolio commands
{
    echo "add_portfolio --name $PORTFOLIO --datafolder $DATA_FOLDER --skip-download"
    echo "switch_portfolio --name $PORTFOLIO"
    
    # Add all assets (data is already downloaded)
    for sym in "${SYMBOLS[@]}"; do
        echo "add_asset --symbol $sym --weight $WEIGHT --skip-download"
    done
    
    echo "echo_marker __TIMER_VAR__"
    echo "compute_var --confidence $CONF --simulations $SIMS"
    echo "echo_marker __TIMER_ES__"
    echo "compute_es --confidence $CONF --simulations $SIMS"
    echo "echo_marker __TIMER_DONE__"
} > "$TMPFILE"

echo "==> Running calculations with ${#SYMBOLS[@]} assets..."
START_TOTAL=$($DATE_CMD +%s%3N)

# Run CLI with timing markers
$CLI interactive < "$TMPFILE" | awk -v start_total="$START_TOTAL" -v date_cmd="$DATE_CMD" '
    function now() {
        cmd = date_cmd " +%s%3N"
        cmd | getline t
        close(cmd)
        return t
    }
    /<<__TIMER_VAR__>>/ {
        start_var = now()
        next
    }
    /<<__TIMER_ES__>>/ {
        end_var = now()
        print "⏱  Time spent computing VaR: " (end_var - start_var) " ms"
        start_es = now()
        next
    }
    /<<__TIMER_DONE__>>/ {
        end_es = now()
        print "⏱  Time spent computing ES:  " (end_es - start_es) " ms"
        print "✅ Total execution time:     " (end_es - start_total) " ms"
        next
    }
    { print }
'
