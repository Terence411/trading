import logging
from ib_insync import IB, Stock

logger = logging.getLogger(__name__)

WATCHLIST = [
    ("SHEL", "SMART", "GBP"),  # Shell
    ("HSBA", "SMART", "GBP"),  # HSBC
    ("BP.",  "SMART", "GBP"),  # BP plc (dot suffix distinguishes LSE listing from NYSE)
    ("AZN",  "SMART", "GBP"),  # AstraZeneca
    ("LLOY", "SMART", "GBP"),  # Lloyds
]


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
