import csv
import logging
import os
import pandas as pd
from ib_insync import IB, Stock

logger = logging.getLogger(__name__)

_WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "input", "watchlist.csv")


def load_watchlist() -> list[tuple[str, str, str]]:
    watchlist = []
    with open(_WATCHLIST_FILE, newline="") as f:
        for row in csv.DictReader(f):
            watchlist.append((row["symbol"], row["exchange"], row["currency"]))
    return watchlist


WATCHLIST = load_watchlist()


class DataFeed:
    def __init__(self, ib: IB):
        self.ib = ib

    def get_snapshot(self) -> list[dict]:
        self.ib.reqMarketDataType(3)  # delayed data, free for all accounts

        contracts = []
        valid_symbols = []
        for symbol, exchange, currency in WATCHLIST:
            contract = Stock(symbol, exchange, currency)
            qualified = self.ib.qualifyContracts(contract)
            if qualified:
                contracts.append(qualified[0])
                valid_symbols.append(symbol)
            else:
                logger.warning(f"Could not qualify contract for {symbol} — skipping.")

        tickers = [self.ib.reqMktData(contract) for contract in contracts]
        self.ib.sleep(6)

        records = []
        for symbol, ticker in zip(valid_symbols, tickers):
            records.append({
                "symbol": symbol,
                "last":   ticker.last   if ticker.last   is not None and ticker.last   > 0 else None,
                "bid":    ticker.bid    if ticker.bid    is not None and ticker.bid    > 0 else None,
                "ask":    ticker.ask    if ticker.ask    is not None and ticker.ask    > 0 else None,
                "close":  ticker.close  if ticker.close  is not None and ticker.close  > 0 else None,
                "volume": int(ticker.volume) if ticker.volume is not None and ticker.volume > 0 else None,
            })

        for contract in contracts:
            self.ib.cancelMktData(contract)

        return records

    def get_candles(self, symbol: str) -> pd.DataFrame:
        contract = Stock(symbol, "SMART", "GBP")
        qualified = self.ib.qualifyContracts(contract)
        if not qualified:
            logger.warning(f"Could not qualify contract for {symbol} — no candles fetched.")
            return pd.DataFrame()

        bars = self.ib.reqHistoricalData(
            qualified[0],
            endDateTime="",
            durationStr="1 D",
            barSizeSetting="15 mins",
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1,
        )
        if not bars:
            logger.warning(f"No historical bars returned for {symbol}.")
            return pd.DataFrame()

        df = pd.DataFrame([{
            "date":   b.date,
            "open":   b.open,
            "high":   b.high,
            "low":    b.low,
            "close":  b.close,
            "volume": b.volume,
        } for b in bars])
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        return df
