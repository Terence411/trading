# IBKR API Error & Warning Code Reference

Codes observed during development. Codes **2000–2999** are informational warnings; codes **outside that range** are errors.

---

## Errors

| Code | Message | Meaning | Action |
|---|---|---|---|
| **200** | No security definition has been found for the request | IBKR cannot find a contract matching the symbol, exchange, and currency provided | Check the symbol spelling. Some LSE stocks need a `.` suffix (e.g. `BP.` instead of `BP`). Try using `SMART` routing and `qualifyContracts()` to resolve the correct contract. |

---

## Warnings (2000–2999)

These are informational — they do not indicate a failure.

| Code | Message | Meaning | Action |
|---|---|---|---|
| **2104** | Market data farm connection is OK:`<farm>` | Connection to the named market data farm is established and healthy | None — this is a confirmation message. |
| **2106** | HMDS data farm connection is OK:`<farm>` | Historical Market Data Server (HMDS) farm is connected | None — informational only. |
| **2108** | Market data farm connection is inactive but should be available upon demand.`<farm>` | The farm is sleeping but will wake up when data is requested | None — it will connect automatically when needed. |
| **2119** | Market data farm is connecting:`<farm>` | The farm is in the process of establishing a connection | None — wait a few seconds; `2104` will follow once connected. |
| **2158** | Sec-def data farm connection is OK:`<farm>` | The security definition farm (used for contract lookups) is connected | None — informational only. |

---

## Warnings (10000+)

| Code | Message | Meaning | Action |
|---|---|---|---|
| **10167** | Requested market data is not subscribed. Displaying delayed market data. | No live market data subscription exists for this contract — IBKR is automatically serving 15–20 min delayed data instead | None — delayed data is free for all accounts. Subscribe to a live data plan in IBKR Account Management if live prices are needed. |

---

## Farm Names

| Farm | Data covered |
|---|---|
| `usfarm` | US equities market data |
| `ushmds` | US historical market data |
| `eufarm` | European (LSE, Euronext, etc.) market data |
| `secdefil` | Security definitions (contract lookups globally) |
