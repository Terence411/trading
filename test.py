from ib_insync import *
import config

ib = IB()
ib.connect(
                host=config.IB_HOST,
                port=config.IB_PORT,
                clientId=config.IB_CLIENT_ID,
                timeout=30,
            )

print("Connected to IBKR API!")
ib.disconnect()