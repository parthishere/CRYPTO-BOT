import sys, os
from market_maker import settings
from market_maker import hotbit
from market_maker import logger

class ExchangeInterface:
    def __init__(self):
        if len(sys.argv) > 1:
            self.symbol = sys.argv[1]
        else:
            self.symbol = settings.SYMBOL
            
        self.hotbit = hotbit.Hotbit(settings.API_KEY, settings.SECRET_KEY)
    
    def get_position(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        self.hotbit.get_balance_query()[symbol]
    
    def get_delta(self, symbol=None):
        if symbol is None:
            symbol = self.symbol
        return self.get_position(symbol)['available']
    
    def get_instrument(self):
        pass


    def get_recent_orders(self):
        return self.hotbit.get_recent_ordersx()
    
    
    def get_highest_buy(self):
        buys = [o for o in self.market_deals() if o['type'] == 'buy']
        if not len(buys):
            return {'price': -2**32}
        highest_buy = max(buys or [], key=lambda o: o['price'])
        return highest_buy if highest_buy else {'price': -2**32}

    def get_lowest_sell(self):
        sells = [o for o in self.market_deals() if o['type'] == 'sell']
        if not len(sells):
            return {'price': 2**32}
        lowest_sell = min(sells or [], key=lambda o: o['price'])
        return lowest_sell if lowest_sell else {'price': 2**32}  # ought to be enough for anyone

    def get_margin(self):
        return self.hotbit.get_balance_query()

    def get_ticker(self, symbol=None):
        """ real time data of symbol  """
        if symbol is None:
            symbol = self.symbol
        return self.hotbit.market_summery(symbol)
        
    def create_bulk_orders(self, orders):
        return self.hotbit.create_bulk_orders(orders)
    
    def get_pending_orders(self):
        return self.hotbit.pending_orders()
    
    def cancel_order(self, order):
        logger.warning("Canceling: %s %d @ %.*f" % (order['side'], order['amount'], order['price']))
        return self.hotbit.order_cancel(order['id'])
    
    def cancel_all_orders(self):
        logger.warning("Resetting current position. Canceling all existing orders.")
        orders = self.hotbit.pending_orders()
        
        if len(orders):
            self.hotbit.bulk_cancel([order['id'] for order in orders])
    
    def cancel_bulk_orders(self, orders):
        for order in orders:
            logger.warning("Canceling: %s %s %d @ %.*f" % (order['id'], order['side'], order['amount'], order['price']))
        return self.hotbit.bulk_cancel([order['id'] for order in orders])
    
    def get_order_book(self):
        pass