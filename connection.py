import logging
from ib_insync import IB

import config

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class IBConnection:
    def __init__(self):
        self.ib = IB()

    def connect(self) -> bool:
        logger.info(
            f"Connecting to IB Gateway at {config.IB_HOST}:{config.IB_PORT} "
            f"(client_id={config.IB_CLIENT_ID})..."
        )
        try:
            self.ib.connect(
                host=config.IB_HOST,
                port=config.IB_PORT,
                clientId=config.IB_CLIENT_ID,
                timeout=30,
            )
            if self.ib.isConnected():
                logger.info("Connection successful.")
                return True
            else:
                logger.error("Connection failed: IB Gateway did not accept the connection.")
                return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()
            logger.info("Disconnected.")

    def is_connected(self) -> bool:
        return self.ib.isConnected()

    def get_account_summary(self):
        if not self.is_connected():
            logger.warning("Not connected — cannot retrieve account summary.")
            return

        account_values = self.ib.accountValues()
        account_id = self.ib.managedAccounts()[0] if self.ib.managedAccounts() else "Unknown"
        logger.info(f"Account: {account_id}")

        currency_symbols = {"USD": "$", "GBP": "£", "EUR": "€"}
        tags_to_show = {"NetLiquidation", "TotalCashValue", "BuyingPower"}
        for av in account_values:
            if av.tag in tags_to_show and av.currency in currency_symbols:
                label = av.tag.replace("NetLiquidation", "Net Liquidation Value") \
                              .replace("TotalCashValue", "Total Cash Value") \
                              .replace("BuyingPower", "Buying Power")
                symbol = currency_symbols[av.currency]
                logger.info(f"  {label}: {symbol}{float(av.value):,.2f}")
