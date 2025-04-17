#!/usr/bin/env bash
set -euo pipefail

# ---------- tweak these two paths if you move files ----------
CLI="python3 ./cli.py"          # the Pybind11 front‑end
DATA_DIR="./data"               # same as in batch_var_es.sh
TRACE_OUT="profile.trace"       # Instruments output
# -------------------------------------------------------------

# ---- parameters copied from your original script ------------
PORTFOLIO="equal_weight"
SIMS=1000000
CONF=0.95
SYMBOLS=(
  AAPL MSFT AMZN GOOG META TSLA JPM V NVDA DIS NFLX ORCL INTC AMD IBM CSCO BA GE F GM
  QCOM TXN MU LRCX ADI AVGO TSM ASML NXPI STX PYPL SHOP COIN TWLO UBER LYFT DASH ABNB Z
  PINS SNAP ETSY EBAY BABA BIDU JD PDD NTES RBLX PLTR CRWD OKTA NET ZS PANW SNOW MDB DDOG
  DOCU ZM TEAM CRM NOW WDAY SAP ADP INTU PAYC ADBE MS GOOGL WFC BAC C GS
  SCHW T VZ TMUS CMCSA TEF NOK ERIC SONY DELL HPQ LEN LOW HD COST WMT TGT
  XOM CVX BP EOG COP SLB HAL OXY PSX VLO MPC ALB
  MMM ABT ABBV ACN AEP AIG ALL AMGN AMP AMT AVB AXP
  BIIB BK BKNG BLK BMY C CAT CB CCI CL CLX CMG COF CVS
  DHR DOW DUK EL EMR ETN EXC FDX GD GILD HON ICE IDXX ILMN
  INFY IP JNJ KHC KMI KSS LMT LULU MA MCD MDT MET MHK MO
  MRK MTB NEE NKE NSC ORLY PFE PG PM PGR PSA RTX SBUX
  SO SPG SPGI TJX TRV TSCO UNH UNP UPS USB VRTX WBA
  ZBH ZBRA ZION ALGN ANET APH BEN BAX BBY CARR CF
  CHTR CMI CTAS CTSH DG DHI
)
# -------------------------------------------------------------

CMD_FILE="cli_cmds.txt"     # unique temp
trap 'rm -f "$CMD_FILE"' EXIT

# ---------- build the interactive command list ---------------
NUM=${#SYMBOLS[@]}
WEIGHT=$(awk -v n="$NUM" 'BEGIN { printf("%.6f", 1/n) }')

{
  echo "add_portfolio --name $PORTFOLIO --datafolder $DATA_DIR"
  echo "switch_portfolio --name $PORTFOLIO"
  for sym in "${SYMBOLS[@]}"; do
    echo "add_asset --symbol $sym --weight $WEIGHT"
  done
  echo "echo_marker __TIMER_VAR__"
  echo "compute_var --confidence $CONF --simulations $SIMS"
  echo "echo_marker __TIMER_ES__"
  echo "compute_es --confidence $CONF --simulations $SIMS"
  echo "echo_marker __TIMER_DONE__"
} >"$CMD_FILE"

echo "📄  Built command script ($NUM assets) → $CMD_FILE"

# ---------- remove old trace if it exists --------------------
rm -rf "$TRACE_OUT"

echo "🚀  Launching Time Profiler on python CLI …"
xcrun xctrace record \
  --template "Time Profiler" \
  --output "$TRACE_OUT" \
  --launch -- /bin/bash -c "$CLI interactive < $CMD_FILE"

echo "✅  Trace saved to $TRACE_OUT"
open "$TRACE_OUT"
