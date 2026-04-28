import pandas as pd


class DataStore:
    def __init__(self):
        self.df = pd.DataFrame()
        self.candles: dict[str, pd.DataFrame] = {}

    def store_snapshot(self, records: list[dict]):
        self.df = (
            pd.DataFrame(records)
            .set_index("symbol")
            .astype({"last": "Float64", "bid": "Float64", "ask": "Float64",
                     "close": "Float64", "volume": "Int64"})
        )

    def store_candles(self, symbol: str, df: pd.DataFrame):
        self.candles[symbol] = df

    def get_opening_range(self, symbol: str) -> tuple[float, float] | None:
        df = self.candles.get(symbol)
        if df is None or len(df) < 2:
            return None
        first_two = df.iloc[:2]
        return float(first_two["high"].max()), float(first_two["low"].min())

    def get_moving_average(self, symbol: str, period: int = 20) -> float | None:
        df = self.candles.get(symbol)
        if df is None or len(df) < period:
            return None
        return float(df["close"].rolling(period).mean().iloc[-1])

    def display(self):
        if self.df.empty:
            print("No data stored.")
            return

        def fmt(val, is_volume=False):
            if pd.isna(val):
                return "—"
            if is_volume:
                return f"{val:,}"
            return f"{val:,.2f}"

        header = f"{'':8}  {'last':>10}  {'bid':>10}  {'ask':>10}  {'close':>10}  {'volume':>12}"
        print(f"\n{header}")
        print("-" * len(header))

        for symbol, row in self.df.iterrows():
            print(
                f"{symbol:<8}  "
                f"{fmt(row['last']):>10}  "
                f"{fmt(row['bid']):>10}  "
                f"{fmt(row['ask']):>10}  "
                f"{fmt(row['close']):>10}  "
                f"{fmt(row['volume'], is_volume=True):>12}"
            )
        print()
