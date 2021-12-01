from market_maker import ordermanager
from market_maker import hotbit, settings, exchange_interface
import requests

ei = exchange_interface.ExchangeInterface()
# print(ei.get_delta())
ordermanager.run()

hb = hotbit.Hotbit()
price = float(ei.market_status(period=settings.LAST_VALUE_PERIOD)['result']['last']) 
# print(
    # ei.create_bulk_orders([
        # {'price':price, 'amount':'0.1', 'side':2},
        # {'price':price, 'amount':'0.11', 'side':2}
        # ])
    # )


# print(hb.order_cancel(order_id=68771353282))
# print(hb.bulk_cancel([67260259658, 67260257682, 67260199569]))

# print(ei.get_pending_orders().get('result').get("CTSUSDT").get('records'))
# orders = ei.get_pending_orders().get('result').get("CTSUSDT").get('records')
# for o in orders:
#     print(o['id'],"\n")

    
# print(hb.get_balance_history())
# print(str(hb.pending_orders())+"\n\n") 
# print(ei.cancel_all_orders())
# print(str(hb.order_finished(side=2))+"\n\n")
# print(hb.order_detail(order_id=66820789291))


# orders = ei.get_pending_orders().get('result').get("CTSUSDT").get('records')
# to_cancel = [o['id'] for o in orders]
# print(ei.cancel_all_orders())
# print(to_cancel)