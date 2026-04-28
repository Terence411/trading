from connection import IBConnection
from data_feed import DataFeed
from data_store import DataStore
from strategy import Strategy
from trader import Trader


def main():
    conn = IBConnection()

    connected = conn.connect()
    if not connected:
        return

    conn.get_account_summary()

    feed = DataFeed(conn.ib)
    records = feed.get_snapshot()

    store = DataStore()
    store.store_snapshot(records)
    store.display()

    trader = Trader(conn.ib)
    Strategy().run_interactive_loop(store, trader)

    conn.disconnect()


if __name__ == "__main__":
    main()
