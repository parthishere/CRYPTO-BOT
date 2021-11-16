from market_maker import ordermanager
from market_maker import hotbit, settings, exchange_interface
import requests

# ei = exchange_interface.ExchangeInterface()
# print(ei.get_delta())
ordermanager.run()


# hb = hotbit.Hotbit()
# print(hb.sell(amount=0.1, price=1.52))
# print(hb.buy(amount=0.1, price=1.50))


# print(hb.get_balance_query())
# print(hb.pending_orders())