import sys, os
import settings


class ExchangeInterface:
    def __init__(self):
        if len(sys.argv) > 1:
            self.symbol = sys.argv[1]
        else:
            self.symbol = settings.SYMBOL
            
        self.hotbit = Hotbit(settings.API_KEY, settings.SECRET_KEY)
    
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
        pass

    def get_ticker(self):
        """ real time data of symbol  """
    
    def market_depth(self):
        return self.hotbit.market_depth()
        
    def create_bulk_orders(self, orders):
        return self.hotbit.create_bulk_orders(orders)
    
    def get_pending_orders(self):
        return self.hotbit.pending_orders()
    
    def cancel_order(self, order):
        return self.hotbit.cancel(order['id'])
    
    def cancel_all_orders(self):
        pass
    
    def cancel_bulk_orders(self, orders):
        return self.hotbit.cancel([order['orderID'] for order in orders])

    