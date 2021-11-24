from market_maker import ordermanager
from market_maker import hotbit, settings, exchange_interface

hb = hotbit.Hotbit()
print(str(hb.pending_orders())+"\n\n") 