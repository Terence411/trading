import logging
import math
from datetime import datetime, time
import pandas as pd
from data_feed import WATCHLIST, DataFeed
from data_store import DataStore
from trader import Trader

logger = logging.getLogger(__name__)

VALID_SYMBOLS = {symbol.upper() for symbol, _, _ in WATCHLIST}

DIVIDER = "\n" + "─" * 50

MENU = f"{DIVIDER}\n  [1] Buy\n  [2] Sell\n  [3] Portfolio\n  [4] Orders\n  [5] Cancel order\n  [6] Run ORB Strategy\n  [7] Quit\n"

MENU_OPTIONS = {"1", "2", "3", "4", "5", "6", "7"}

EOD_TIME   = time(16, 20)
MARKET_OPEN = time(8, 0)
ORB_END    = time(8, 30)


class ORBStrategy:
    TRADE_AMOUNT  = 5000   # £ per trade
    PROFIT_TARGET = 1.015  # +1.5%
    STOP_LOSS     = 0.9925 # -0.75%
    MA_PERIOD     = 20
    POLL_INTERVAL = 60     # seconds between price checks

    def run(self, feed: DataFeed, store: DataStore, trader: Trader):
        now = datetime.now().time()

        if now < MARKET_OPEN:
            print("  Market has not opened yet (opens 08:00 UK).")
            return
        if now < ORB_END:
            print("  Opening range not yet established — please run after 08:30 UK.")
            return
        if now >= EOD_TIME:
            print("  Too close to market close to run the strategy today.")
            return

        print(f"\n  Scanning {len(WATCHLIST)} symbols for ORB breakouts...\n")

        buy_list = []
        for symbol, _, _ in WATCHLIST:
            df = feed.get_candles(symbol)
            if df.empty:
                continue
            store.store_candles(symbol, df)

            orb = store.get_opening_range(symbol)
            if orb is None:
                logger.warning(f"{symbol}: not enough bars to establish opening range.")
                continue

            orb_high, _ = orb
            current_price = float(df["close"].iloc[-1])

            logger.info(f"{symbol}: ORB high={orb_high:.2f}  current={current_price:.2f}")
            if current_price > orb_high:
                shares = math.floor(self.TRADE_AMOUNT / current_price)
                if shares > 0:
                    buy_list.append((symbol, current_price, shares))

        if not buy_list:
            print("  No ORB breakout signals found.\n")
            return

        print(f"\n  {len(buy_list)} breakout(s) found:\n")
        for symbol, price, shares in buy_list:
            print(f"    {symbol}  price={price:.2f}  shares={shares}  cost=£{price * shares:,.2f}")

        confirm = input("\n  Place buy orders for all? (yes / no): ").strip().lower()
        if confirm != "yes":
            print("  Cancelled.")
            return

        open_positions: dict[str, dict] = {}
        available = trader.get_available_funds()

        for symbol, price, shares in buy_list:
            cost = price * shares
            if cost > available:
                logger.warning(f"{symbol}: insufficient funds (need £{cost:,.2f}, have £{available:,.2f}) — skipping.")
                continue
            result = trader.place_order(symbol, "BUY", shares)
            if result:
                entry = result.get("avg_fill_price") or price
                open_positions[symbol] = {"entry": entry, "shares": shares}
                available -= cost

        if not open_positions:
            print("  No orders were placed.\n")
            return

        print(f"\n  Monitoring {len(open_positions)} position(s). Checking every {self.POLL_INTERVAL}s. Press Ctrl+C to stop.\n")

        try:
            while open_positions:
                feed.ib.sleep(self.POLL_INTERVAL)
                now = datetime.now().time()

                to_close = []
                for symbol, pos in open_positions.items():
                    df = feed.get_candles(symbol)
                    if df.empty:
                        continue
                    store.store_candles(symbol, df)

                    current = float(df["close"].iloc[-1])
                    entry   = pos["entry"]
                    shares  = pos["shares"]
                    ma      = store.get_moving_average(symbol, self.MA_PERIOD)

                    reason = None
                    if current >= entry * self.PROFIT_TARGET:
                        reason = f"profit target hit ({current:.2f} >= {entry * self.PROFIT_TARGET:.2f})"
                    elif current <= entry * self.STOP_LOSS:
                        reason = f"stop loss hit ({current:.2f} <= {entry * self.STOP_LOSS:.2f})"
                    elif ma is not None and current < ma:
                        reason = f"MA breakdown ({current:.2f} < MA {ma:.2f})"
                    elif now >= EOD_TIME:
                        reason = "end of day exit"

                    if reason:
                        logger.info(f"{symbol}: selling {shares} shares — {reason}")
                        trader.place_order(symbol, "SELL", shares)
                        pnl = (current - entry) * shares
                        logger.info(f"{symbol}: estimated P&L = £{pnl:+,.2f}")
                        to_close.append(symbol)
                    else:
                        logger.info(f"{symbol}: holding — price={current:.2f}  entry={entry:.2f}  MA={ma:.2f if ma else '—'}")

                for symbol in to_close:
                    del open_positions[symbol]

                if now >= EOD_TIME and open_positions:
                    logger.info("EOD reached — closing all remaining positions.")
                    trader.close_all_positions()
                    break

        except KeyboardInterrupt:
            print("\n  Strategy stopped by user.")
            if open_positions:
                close = input("  Close all open positions now? (yes / no): ").strip().lower()
                if close == "yes":
                    trader.close_all_positions()

        print("\n  ORB strategy session ended.\n")


class Strategy:
    def run_interactive_loop(self, store: DataStore, trader: Trader, feed: DataFeed):
        while True:
            print(MENU)
            choice = input("Select an option: ").strip()

            if choice not in MENU_OPTIONS:
                print(f"{DIVIDER}\n  Invalid option. Enter a number from 1 to 7.")
                continue

            if choice == "7":
                break

            if choice == "3":
                print(DIVIDER)
                trader.display_portfolio()
                continue

            if choice == "4":
                print(DIVIDER)
                trader.display_orders()
                continue

            if choice == "5":
                print(DIVIDER)
                trader.cancel_order()
                continue

            if choice == "6":
                print(DIVIDER)
                ORBStrategy().run(feed, store, trader)
                continue

            action = "buy" if choice == "1" else "sell"

            print(DIVIDER)
            symbol = input("Enter symbol: ").strip().upper()
            if symbol not in VALID_SYMBOLS:
                print(f"  '{symbol}' is not in the watchlist. Valid symbols: {', '.join(sorted(VALID_SYMBOLS))}")
                continue

            qty_input = input("Enter quantity: ").strip()
            try:
                quantity = int(qty_input)
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                print("  Quantity must be a positive whole number.")
                continue

            if action == "sell":
                positions = trader.get_positions()
                held = positions.get(symbol, 0)
                if held < quantity:
                    print(f"  Insufficient shares. You hold {int(held)} share(s) of {symbol}, cannot sell {quantity}.")
                    continue

            if action == "buy":
                row = store.df.loc[symbol] if symbol in store.df.index else None
                price = None
                if row is not None:
                    price = row["last"] if not pd.isna(row["last"]) else row["close"]

                if price is None or pd.isna(price):
                    print(f"  Cannot determine current price for {symbol} — no market data available.")
                    continue

                total_cost = price * quantity
                available = trader.get_available_funds()
                if total_cost > available:
                    print(f"  Insufficient funds. Required: £{total_cost:,.2f} | Available: £{available:,.2f}")
                    continue

            print()
            trader.place_order(symbol, action, quantity)
            print()
