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

`get_account_summary()` displays the following fields (in GBP, USD, or EUR): Net Liquidation Value, Total Cash Value, Buying Power, Available Funds, Excess Liquidity. To add more tags, extend `tags_to_show`. To add another currency, extend `currency_symbols`.

---

## `main.py`

Entry point. Connects to IB Gateway, prints the account summary, fetches a price snapshot for the watchlist, then disconnects.

---

## `data_feed.py`

Fetches a one-time price snapshot for a fixed watchlist of LSE stocks.

**`WATCHLIST`** — module-level list of `(symbol, exchange, currency)` tuples. Edit this to change which stocks are tracked.

### `DataFeed`

| Method | Description |
|---|---|
| `__init__(ib)` | Takes the `ib_insync.IB` instance from `IBConnection.ib` |
| `get_snapshot()` | Requests delayed market data for all watchlist symbols, waits 6 seconds, prints a formatted price table, then cancels subscriptions |

Uses `reqMarketDataType(3)` (delayed, 15–20 min) by default — free for all accounts. Change to `1` for live data if a market data subscription is active. Fields displayed: Last, Bid, Ask, Close, Volume. Missing values (outside market hours) are shown as `—`.

---

## `data_store.py`

Owns the pandas DataFrame that holds the current price snapshot. Other modules (strategy, trader) read from `DataStore.df` directly.

### `DataStore`

| Method / Attribute | Description |
|---|---|
| `df` | The underlying `pd.DataFrame`, indexed by symbol with columns: `last`, `bid`, `ask`, `close`, `volume` |
| `store_snapshot(records)` | Takes the `list[dict]` returned by `DataFeed.get_snapshot()` and builds the DataFrame |
| `display()` | Prints a formatted table of the DataFrame. NaN values shown as `—` |

---

## `strategy.py`

Runs the interactive prompt loop. Validates user input and delegates order execution to `Trader`.

### `Strategy`

| Method | Description |
|---|---|
| `run_interactive_loop(trader)` | Loops: prompts for action (buy/sell/quit), symbol, and quantity. Validates each input then calls `trader.place_order()`. |

Valid symbols are derived from `WATCHLIST` in `data_feed.py`. Input is case-insensitive.

---

## `trader.py`

Executes orders against the IBKR paper trading account.

### `Trader`

| Method | Returns | Description |
|---|---|---|
| `place_order(symbol, action, quantity)` | `dict` | Qualifies the contract, creates a `MarketOrder`, places it via `ib.placeOrder()`, waits 2 seconds, and logs the status. Returns `{"status", "filled", "avg_fill_price"}`. |

Outside market hours, `status` will be `Submitted` or `PreSubmitted` — the order is queued and will execute when the LSE opens.

---

## Dependency flow

```
main.py
  ├── connection.py
  │     └── config.py
  │           └── .env
  └── data_feed.py

(future)
main.py
  ├── data_store.py  ──► data_feed.py
  ├── strategy.py    ──► data_store.py
  └── trader.py      ──► connection.py, strategy.py
```
