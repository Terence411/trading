import logging
from ib_insync import IB, Stock, MarketOrder

logger = logging.getLogger(__name__)


class Trader:
    def __init__(self, ib: IB):
        self.ib = ib

    def get_positions(self) -> dict[str, float]:
        return {pos.contract.symbol: pos.position for pos in self.ib.positions()}

    def get_available_funds(self) -> float:
        for av in self.ib.accountValues():
            if av.tag == "AvailableFunds" and av.currency == "GBP":
                return float(av.value)
        return 0.0

    def display_portfolio(self):
        items = self.ib.portfolio()
        if not items:
            print("\n  No open positions.\n")
            return

        header = f"\n{'Symbol':<8}  {'Qty':>8}  {'Avg Cost':>10}  {'Mkt Price':>10}  {'Mkt Value':>12}  {'Unrealised P&L':>16}  {'Realised P&L':>14}"
        print(header)
        print("-" * len(header))
        for item in items:
            symbol    = item.contract.symbol
            qty       = int(item.position)
            avg_cost  = f"£{item.averageCost:,.2f}"
            mkt_price = f"£{item.marketPrice:,.2f}"
            mkt_value = f"£{item.marketValue:,.2f}"
            unreal    = f"£{item.unrealizedPNL:,.2f}"
            real      = f"£{item.realizedPNL:,.2f}"
            print(f"{symbol:<8}  {qty:>8}  {avg_cost:>10}  {mkt_price:>10}  {mkt_value:>12}  {unreal:>16}  {real:>14}")
        print()

    def display_orders(self):
        trades = self.ib.trades()
        if not trades:
            print("\n  No orders this session.\n")
            return

        header = f"\n{'Symbol':<8}  {'Action':<6}  {'Qty':>6}  {'Type':<6}  {'Status':<16}  {'Filled':>8}  {'Avg Price':>10}"
        print(header)
        print("-" * len(header))
        for trade in trades:
            symbol    = trade.contract.symbol
            action    = trade.order.action
            qty       = int(trade.order.totalQuantity)
            order_type = trade.order.orderType
            status    = trade.orderStatus.status
            filled    = int(trade.orderStatus.filled)
            avg_price = f"£{trade.orderStatus.avgFillPrice:,.2f}" if trade.orderStatus.avgFillPrice else "—"
            print(f"{symbol:<8}  {action:<6}  {qty:>6}  {order_type:<6}  {status:<16}  {filled:>8}  {avg_price:>10}")
        print()

    def cancel_order(self):
        pending = [
            t for t in self.ib.trades()
            if t.orderStatus.status in ("PreSubmitted", "Submitted")
        ]
        if not pending:
            print("\n  No pending orders to cancel.\n")
            return

        print()
        for i, trade in enumerate(pending, start=1):
            symbol = trade.contract.symbol
            action = trade.order.action
            qty    = int(trade.order.totalQuantity)
            status = trade.orderStatus.status
            print(f"  [{i}] {action} {qty} {symbol}  —  {status}")
        print()

        selection = input("Enter order number to cancel (or 'back' to return): ").strip()
        if selection.lower() == "back":
            return

        try:
            index = int(selection) - 1
            if not (0 <= index < len(pending)):
                raise ValueError
        except ValueError:
            print("  Invalid selection.")
            return

        trade = pending[index]
        self.ib.cancelOrder(trade.order)
        self.ib.sleep(1)

        updated_status = trade.orderStatus.status
        logger.info(
            f"Cancel requested: {trade.order.action} {int(trade.order.totalQuantity)} "
            f"{trade.contract.symbol} — Status: {updated_status}"
        )
        print()

    def place_order(self, symbol: str, action: str, quantity: int) -> dict:
        contract = Stock(symbol, "SMART", "GBP")
        qualified = self.ib.qualifyContracts(contract)
        if not qualified:
            logger.error(f"Could not qualify contract for {symbol} — order not placed.")
            return {}

        order = MarketOrder(action.upper(), quantity)
        trade = self.ib.placeOrder(qualified[0], order)
        self.ib.sleep(2)

        status = trade.orderStatus.status
        filled = trade.orderStatus.filled
        avg_price = trade.orderStatus.avgFillPrice

        logger.info(f"Order placed: {action.upper()} {quantity} {symbol} @ MKT")
        logger.info(f"Status: {status} | Filled: {filled} | Avg price: {avg_price}")

        return {"status": status, "filled": filled, "avg_fill_price": avg_price}
