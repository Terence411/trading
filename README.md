# Trading Bot

An automated day trading application built in Python, connected to Interactive Brokers via IB Gateway.

## Requirements

- Python 3.10+
- IB Gateway (paper or live) running on Windows
- IBKR Pro account with paper trading enabled

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
IB_HOST=172.20.144.1   # Windows host IP (see WSL2 note below)
IB_PORT=4002            # 4002 = paper trading, 4001 = live
IB_CLIENT_ID=1
```

## Running

```bash
python main.py
```

## IB Gateway Configuration

1. Open IB Gateway and log in with your paper trading account
2. Go to **Configure → Settings → API → Settings**
   - Confirm socket port is `4002`
   - Add trusted IPs (see WSL2 note below)

## WSL2 Note

If running Python inside WSL2, `127.0.0.1` will not reach IB Gateway on Windows. You need the Windows host IP instead.

```bash
# Get Windows host IP (use this as IB_HOST)
ip route show | grep default

# Get WSL2 IP (add this to IB Gateway trusted IPs)
ip addr show eth0 | grep inet
```

Add **both** IPs to IB Gateway's Trusted IP Addresses list, then restart IB Gateway.

## Phases

| Phase | Status | Description |
|---|---|---|
| 1 | Done | Connect to IB Gateway and verify account |
| 2 | Done | Fetch delayed price snapshot for LSE watchlist (SHEL, HSBA, BP., AZN, LLOY) |
| 3 | Done | Structure snapshot data into a pandas DataFrame |
| 4 | Done | Interactive buy/sell market orders against paper account |
