from market_maker import ordermanager
from market_maker import hotbit, settings, exchange_interface
import requests

hb = hotbit.Hotbit()
print(hb.pending_orders())

hb = hotbit.Hotbit()
print(hb.get_balance_history())

hb = hotbit.Hotbit()
print(hb.order_finished())

hb = hotbit.Hotbit()
print(hb.get_balance_query())
