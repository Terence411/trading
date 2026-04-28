# Future Changes

Things to address when moving from paper/development to a live production setup.

---

## Market Data

| Item | Current state | What to change |
|---|---|---|
| **Data type** | Delayed (15–20 min) via `reqMarketDataType(3)` in `data_feed.py` | Change to `reqMarketDataType(1)` for live data after subscribing to LSE market data through IBKR Client Portal |
| **Bid/Ask prices** | Empty outside market hours; absent with delayed data | Will populate automatically once on a live data subscription |
| **Watchlist** | Hardcoded list in `data_feed.py` | Move to a config file or database so symbols can be changed without touching code |
| **BP. ticker suffix** | `BP.` used to disambiguate BP plc on LSE from other exchanges | Audit all symbols — other LSE stocks may have similar quirks. Always use `qualifyContracts()` to verify. |

---

## Connection & Infrastructure

| Item | Current state | What to change |
|---|---|---|
| **Trading account** | Paper account (`DUO743651`) on port `4002` | Change `IB_PORT` in `.env` to `4001` for live trading. Double-check all order logic before switching. |
| **WSL2 host IP** | `IB_HOST` in `.env` set to Windows host IP, which can change on reboot | Either assign a static IP to the WSL2 adapter on Windows, or add a startup script that detects and updates `IB_HOST` automatically |
| **Reconnection logic** | No retry — if the connection drops, the app exits | Add a reconnection loop with backoff for a production setup |
| **Connection timeout** | 30 seconds — generous for development | Tune down once stable; add alerting if connection takes too long |

---

## Data Fetching

| Item | Current state | What to change |
|---|---|---|
| **Snapshot wait** | `ib.sleep(6)` — waits a fixed 6 seconds for data to arrive | Replace with event-driven logic that waits until data is actually received, not a fixed delay |
| **Data fetch mode** | One-time snapshot (Phase 2) | Phase 3 will move to continuous streaming with data stored in DataFrames |

---

## Account & Financials

| Item | Current state | What to change |
|---|---|---|
| **Supported currencies** | GBP, USD, EUR hardcoded in `connection.py` | Review if trading in markets with other currencies (e.g. HKD, JPY) |
| **Order precautions** | Not yet configured | Before live trading, review IB Gateway's order precaution settings (Configure → API → Precautions) to avoid accidental large orders |

---

## Phases Not Yet Built

| Phase | Description |
|---|---|
| **Phase 3** | ~~Store streaming price data in pandas DataFrames~~ ✅ Done |
| **Phase 4** | Manual buy/sell order execution against the paper account |
