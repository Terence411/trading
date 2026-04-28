import logging
import pandas as pd
from data_feed import WATCHLIST
from data_store import DataStore
from trader import Trader

logger = logging.getLogger(__name__)

VALID_SYMBOLS = {symbol.upper() for symbol, _, _ in WATCHLIST}

DIVIDER = "\n" + "─" * 50

MENU = f"{DIVIDER}\n  [1] Buy\n  [2] Sell\n  [3] Portfolio\n  [4] Orders\n  [5] Cancel order\n  [6] Quit\n"

MENU_OPTIONS = {"1", "2", "3", "4", "5", "6"}


class Strategy:
    def run_interactive_loop(self, store: DataStore, trader: Trader):
        while True:
            print(MENU)
            choice = input("Select an option: ").strip()

            if choice not in MENU_OPTIONS:
                print(f"{DIVIDER}\n  Invalid option. Enter a number from 1 to 6.")
                continue

            if choice == "6":
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
