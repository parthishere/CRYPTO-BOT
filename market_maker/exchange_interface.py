import sys, os
from market_maker import settings
from market_maker import hotbit
import logging

logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')


class ExchangeInterface():
    def __init__(self):
        if len(sys.argv) > 1:
            self.symbol = sys.argv[1]
        else:
            self.symbol = settings.ASSET
            
        self.hotbit = hotbit.Hotbit(api_key=settings.API_KEY, secret_key=settings.SECRET_KEY, symbol=settings.ASSETS)
    
    def get_position(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        return self.hotbit.get_balance_query()['result'][symbol]
    
    def get_delta(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        return float(self.get_position(symbol)['available'])
    
    def get_instrument(self):
        pass


    def get_recent_order_bids(self):
        return self.hotbit.get_recent_order_bids()
    
    def get_recent_order_sells(self):
        return self.hotbit.get_recent_order_sells()
    
    
    def get_highest_buy(self):
        buys = [o for o in self.get_recent_order_bids()['result']['orders']]  #2 for buy
        if not len(buys):
            return -2**32
        highest_buy = float(max(buys or [], key=lambda o: float(o['price']))['price'])
        return highest_buy if highest_buy else -2**32

    def get_lowest_sell(self):
        sells = [o for o in self.get_recent_order_sells()['result']['orders']]    #1 for sell
        if not len(sells):
            return 2**32
        lowest_sell = float(min(sells or [], key=lambda o: float(o['price']))['price'])
        return lowest_sell if lowest_sell else 2**32  # ought to be enough for anyone

    def get_margin(self):
        return self.hotbit.get_balance_query()

    def get_ticker(self, symbol=None):
        """ real time data of symbol  """
        if symbol is None:
            symbol = self.symbol
        return self.hotbit.market_summery(symbol)
        
    def create_bulk_orders(self, orders):
        for order in orders:
            if order['side'] == 1:  # 1-Seller，2-buyer
                return self.hotbit.sell(amount=order['amount'], price=order['price'])
            elif order['side'] == 2:  # 1-Seller，2-buyer
                return self.hotbit.buy(amount=order['amount'], price=order['price'])
        
    
    def get_pending_orders(self):
        return self.hotbit.pending_orders()
    
    def cancel_order(self, order):
        logging.warning("Canceling:%d %s %d @ %.*f" % (order['id'], order['side'], order['amount'], order['price']))
        return self.hotbit.order_cancel(order['id'])
    
    def cancel_all_orders(self):
        logging.warning("Resetting current position. Canceling all existing orders.")
        orders = self.hotbit.pending_orders()
        
        try:
            if len(orders):
                return self.hotbit.bulk_cancel([order['id'] for order in orders])
        except Exception as e:
            print(e)
            return e
    
    def cancel_bulk_orders(self, orders):
        for order in orders:
            logging.warning("Canceling: %s %s %d @ %.*f" % (order['id'], order['side'], order['amount'], order['price']))
        return self.hotbit.bulk_cancel([order['id'] for order in orders])
    
    def market_status(self, period=settings.LAST_VALUE_PERIOD):
        return self.hotbit.market_status(period=period)
