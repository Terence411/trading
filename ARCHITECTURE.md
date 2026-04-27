# Architecture

Technical reference for the components in this codebase.

---

## `config.py`

Loads connection settings from the `.env` file using `python-dotenv` and exposes them as module-level constants.

| Variable | Type | Default | Description |
|---|---|---|---|
| `IB_HOST` | `str` | `127.0.0.1` | IP address of the machine running IB Gateway |
| `IB_PORT` | `int` | `4002` | API port (4002 = paper, 4001 = live) |
| `IB_CLIENT_ID` | `int` | `1` | Unique client ID for this connection |

All other modules import from `config` directly — no module reads `.env` itself.

---

## `connection.py`

Owns the lifecycle of the IBKR API connection. Built around the `IBConnection` class which wraps `ib_insync.IB`.

### `IBConnection`

| Method | Returns | Description |
|---|---|---|
| `connect()` | `bool` | Connects to IB Gateway using settings from `config`. Returns `True` on success. |
| `disconnect()` | `None` | Cleanly disconnects if currently connected. |
| `is_connected()` | `bool` | Returns current connection state. |
| `get_account_summary()` | `None` | Logs account ID and key balance fields (Net Liquidation, Cash, Buying Power). |

**`self.ib`** — the underlying `ib_insync.IB` instance. All future phases that need to make API calls (market data, orders) should access this via the `IBConnection` object.

`get_account_summary()` currently displays values in GBP, USD, and EUR. To add another currency, extend `currency_symbols` in that method.

---

## `main.py`

Entry point. Instantiates `IBConnection`, runs the connection check, prints the account summary, then disconnects. Serves as the Phase 1 verification script — will grow into the main application loop in later phases.

---

## `data_feed.py` *(Phase 2 — not yet implemented)*

Will handle live price streaming for a watchlist of stock symbols using `ib_insync` market data subscriptions (`reqMktData` / `reqTickByTick`).

---

## `data_store.py` *(Phase 3 — not yet implemented)*

Will manage in-memory storage of price data using `pandas` DataFrames — tick data, OHLCV bars, and any derived columns needed by the strategy.

---

## `strategy.py` *(Phase 4 — not yet implemented)*

Will contain the buy/sell signal logic. Phase 4 starts with manual order invocation (user-triggered), with the option to add automated signal generation later.

---

## `trader.py` *(Phase 4 — not yet implemented)*

Will execute orders against the paper trading account via `ib_insync` order placement APIs. Works alongside `strategy.py` — strategy generates the signal, trader executes it.

---

## Dependency flow

```
main.py
  └── connection.py
        └── config.py
              └── .env

(future)
main.py
  ├── data_feed.py   ──► connection.py
  ├── data_store.py  ──► data_feed.py
  ├── strategy.py    ──► data_store.py
  └── trader.py      ──► connection.py, strategy.py
```
