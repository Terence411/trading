# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
# Run the app (IB Gateway must be running first)
python main.py
```

## IB Gateway

- Paper trading port: `4002` | Live trading port: `4001`
- Connection settings are in `.env` (not committed). Defaults: `172.20.144.1:4002`, client_id `1`
- Running on WSL2: `IB_HOST` must be the Windows host IP, not `127.0.0.1`
  - Windows host IP: `ip route show | grep default` (the `via` address)
  - WSL2 IP: `ip addr show eth0 | grep inet`
  - Both IPs must be added to IB Gateway's Trusted IP list
- API settings in IB Gateway: Configure → Settings → API → Settings
  - Socket API is enabled by default in newer IB Gateway versions (10+)
  - Trusted IPs: add both the Windows host IP and WSL2 IP

## Architecture

| File | Purpose |
|---|---|
| `config.py` | Loads `IB_HOST`, `IB_PORT`, `IB_CLIENT_ID` from `.env` |
| `connection.py` | `IBConnection` wraps `ib_insync.IB` — connect, disconnect, account summary |
| `main.py` | Entry point — connects, prints account info, disconnects |
| `data_feed.py` | (Phase 2) Live price streaming |
| `data_store.py` | (Phase 3) Pandas DataFrame management |
| `strategy.py` | (Phase 4) Buy/sell signal logic |
| `trader.py` | (Phase 4) Order execution |

## Account

- Paper trading account: `DUO743651` (denominated in GBP)
- `get_account_summary()` filters for GBP, USD, and EUR — add currencies to `currency_symbols` in `connection.py` if needed

## Key library

`ib_insync` wraps IBKR's official `ibapi` with an asyncio-friendly interface. All IBKR interactions go through `IBConnection.ib` (an `ib_insync.IB` instance).
