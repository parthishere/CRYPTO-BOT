import datetime, sys, math, random
from market_maker import settings
from .exchange_interface import ExchangeInterface
    
from os.path import getmtime
import logging
from time import sleep


import os
watched_files_mtimes = [(f, getmtime(f)) for f in settings.WATCHED_FILES]

logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')



class OrderManager:
    def __init__(self):
        self.exchange = ExchangeInterface()
        # Once exchange is created, register exit handler that will always cancel orders
        # on any error.
        settings.get_input_range()
        logging.info("Using symbol %s." % self.exchange.symbol)

        logging.info("Order Manager initializing, connecting to BitMEX. Live run: executing real trades.")
        if settings.DEBUG:
            logging.info("Initializing dry run. Orders printed below represent what would be posted to Hotbit.")
        else:
            logging.info("Order Manager initializing, connecting to Hotbit. Live run: executing real trades.")
        
        self.start_time = datetime.datetime.now()
        self.starting_qty = float(self.exchange.get_delta())
        self.running_qty = float(self.starting_qty)
        
        self.get_lowest_sell = self.exchange.get_lowest_sell()
        self.get_highest_buy = self.exchange.get_highest_buy()
        
        
        self.reset()

    def reset(self):
        self.exchange.cancel_all_orders()
        self.print_status()

        # Create orders and converge.
        self.place_orders()

    def print_status(self):
        """Print the current MM status."""

        margin = self.exchange.get_delta()
        self.running_qty = float(self.exchange.get_delta())
        logging.info("highest bid = %f", self.get_highest_buy)
        logging.info("lowest sell = %f", self.get_lowest_sell)
        logging.info("Input Range: %f - %fs" % (settings.INPUT_LOWER_RANGE, settings.INPUT_UPPER_RANGE))
        logging.info("Delta : %s" % str(self.exchange.get_delta()))
        logging.info("Position in CTS: %s" % str(self.exchange.get_position()))
        # logging.info("Current Contract Position: %d" % self.running_qty)
        if settings.CHECK_POSITION_LIMITS:
            logging.info("Position limits: %d/%d" % (settings.MIN_POSITION, settings.MAX_POSITION))
       
        logging.info("Contracts Traded This Run: %d" % (self.running_qty - self.starting_qty))
        # hard coded
        logging.info("Pending orders : %s" % str(self.exchange.get_pending_orders().get('result').get("CTSUSDT").get('records')))
        logging.info("Trading Type : %s" % settings.TYPE)
        logging.info("Current Crypto Price: %f" %self.exchange.get_crypto_price())
        
        

    def get_price_offset(self, index, order_pairs):
        """Given an index (1, -1, 2, -2, etc.) return the price for that side of the book.
           Negative is a buy, positive is a sell."""
        # Maintain existing spreads for max profit
        ############### CHECK THIS OUT ###############
        prices = []
        if settings.BUY_AGGRESIVELY:
            SPREAD = settings.MAX_SPREAD
        else:
            SPREAD = settings.MIN_SPREAD
        price = self.recent_price
        
        if index == 1:
            # sell
            for i in range(0, order_pairs):
                prices.append(settings.INPUT_UPPER_RANGE)
        else:
            # buy
            for i in range(0, order_pairs):
                prices.append(settings.INPUT_LOWER_RANGE)

        print(prices)
        return prices

    ###
    # Orders
    ###

    def place_orders(self):
        """Create order items for use in convergence."""
        
        buy_orders = []
        sell_orders = []
        # Create orders from the outside in. This is intentional - let's say the inner order gets taken;
        # then we match orders from the outside in, ensuring the fewest number of orders are amended and only
        # a new order is created in the inside. If we did it inside-out, all orders would be amended
        # down and a new order would be created at the outside.
        # for i in reversed(range(1, settings.ORDER_PAIRS + 1)):
        #     if not self.long_position_limit_exceeded():
        #         buy_orders.append(self.prepare_order(-i))
        #     if not self.short_position_limit_exceeded():
        #         sell_orders.append(self.prepare_order(i))
        # for fifteen days seconds are 15*24*60*60 = 1296000
        # period = 1296000
        # result = self.exchange.market_status(period=1296000)
        self.recent_price = recent_value = self.exchange.get_crypto_price()
        
        recent_buy_orders = self.exchange.get_recent_order_bids()['result']['orders']
        recent_sell_orders = self.exchange.get_recent_order_sells()['result']['orders']
        bid_amount = 0
        sell_amount = 0
        buy_orders = None
        sell_orders = None                  
        for result in recent_buy_orders:
            if result['side'] == 2:    # 2 for buy
                bid_amount += float(result['amount'])
        for result in recent_sell_orders:
            if result['side'] == 1:
                sell_amount += float(result['amount'])
        
        logging.info("bid amount = %d , sell amount = %d",bid_amount ,sell_amount)
        if recent_value <= settings.INPUT_LOWER_RANGE or recent_value >= settings.INPUT_UPPER_RANGE :
            if settings.TYPE == "VOLUME":
                    if abs(bid_amount - sell_amount)*100 / min(bid_amount, sell_amount) > settings.FLUCTUATION :
                        if bid_amount > sell_amount:
                            print("buyer is greater than seller sell some volume")
                            change = abs(bid_amount - sell_amount)
                            index = 1 # 1 for selling
                            change_in_price = (self.recent_price - settings.INPUT_UPPER_RANGE)
                            buy_orders = self.prepare_order(index, amount=change, change_in_price=change_in_price)
                        elif bid_amount < sell_amount:
                            print("seller are grater than buyer, buy some volume..")
                            change = abs(sell_amount - bid_amount)
                            change_in_price = (self.recent_price - settings.INPUT_LOWER_RANGE)
                            index = 2 # 2 for buying
                            sell_orders = self.prepare_order(index, amount=change, change_in_price=change_in_price)
                    else:
                        print("Volume is under Fluctuation")
                        
            elif settings.TYPE == "PRICE":
                if recent_value < settings.INPUT_LOWER_RANGE:
                    change = abs(bid_amount - sell_amount)
                    if change == 0:
                        change = settings.DEFAULT_CHANGE
                    index = 2 # 2 for buying
                    change_in_price = (self.recent_price - settings.INPUT_LOWER_RANGE)
                    buy_orders = self.prepare_order(index, amount=change, change_in_price=change_in_price)
                    logging.info("Recent value is less than input range Buying some amount..")
                elif recent_value > settings.INPUT_UPPER_RANGE:
                    change = abs(bid_amount - sell_amount)
                    if change == 0:
                        change = settings.DEFAULT_CHANGE
                    index = 1 # 1 for selling
                    change_in_price = (self.recent_price - settings.INPUT_UPPER_RANGE)
                    buy_orders = self.prepare_order(index, amount=change, change_in_price=change_in_price)
                    logging.info("Recent value is greater than input range Selling some amount..")
                else:
                    print("SELLER ARE EQUAL TO BUYER.. NOTHING TO DO")
                    
            return self.converge_orders(buy_orders, sell_orders)      
        
        
                

        

    def prepare_order(self, index, amount, change_in_price):
        """Create an order object."""
        # change
        # orderQty = round((amount / settings.MAX_ORDER_PAIRS**2)*change_in_price, 2)
        orderQty = round((amount/settings.MAX_ORDER_PAIRS)*(change_in_price**2), 2)
        orders = []
        
        prices = self.get_price_offset(index, settings.MAX_ORDER_PAIRS)
        position = prices[0] * orderQty * settings.MAX_ORDER_PAIRS
        for i in range(0, settings.MAX_ORDER_PAIRS):
            orders.append({'price': str(prices[i]), 'amount': str(abs(orderQty)), 'side': index})
            
        if index is 1:
            logging.info("\nContract that will be traded in this run : %s USDT, Current position: %s " % (str(position), str(self.exchange.get_position())))
            logging.info("\nCTS that will be sold this trade: %s" % str(orderQty * settings.MAX_ORDER_PAIRS))
        else:
            logging.info("\nContract that will be traded in this run : %s USDT, Current position: %s " % (str(position), str(self.exchange.get_position())))
            logging.info("\nCTS that will be bought this trade: %s" % str(orderQty * settings.MAX_ORDER_PAIRS))
            if self.check_usdt(position):
                logging.error("Not enough Balance, Resetting bot")
                self.reset()
        # print(orders)
        return orders

    def converge_orders(self, buy_orders, sell_orders):
        """Converge the orders we currently have in the book with what we want to be in the book.
           This involves amending any open orders and creating new ones if any have filled completely.
           We start from the closest orders outward."""

        # tickLog = self.exchange.get_instrument()['tickLog']
        to_amend = []
        to_create = []
        to_cancel = []
        buys_matched = 0
        sells_matched = 0
        existing_user_orders = []
        try:
            existing_user_orders = self.exchange.get_pending_orders().get('result').get(self.exchange.symbol).get('records')
        except:
            pass
        


        # Check all existing orders and match them up with what we want to place.
        # If there's an open one, we might be able to amend it to fit what we want.
        if existing_user_orders:
            desired_order = None
            for order in existing_user_orders:
                
                
                if order['side'] == 1:   # 1-Seller，2-buyer
                    # for seller
                    if sell_orders:
                        desired_order = sell_orders[sells_matched]
                        sells_matched +=1
                    else:
                        logging.info("previously sell orders were placed now buy orders are being placed")
                        
                else:   # 1-Seller，2-buyer
                    # for buyer
                    if buy_orders:
                        desired_order = buy_orders[sells_matched]
                        buys_matched +=1
                    else:
                        logging.info("previously sell orders were placed now buy orders are being placed")
                        
                if desired_order['amount'] != order['left'] or (abs((float(desired_order['price']) / float(order['price'])) - 1) > settings.RELIST_INTERVAL):
                    to_amend.append({'id': order['id'], 'amount': str(order['left'] + desired_order['amount']),
                                        'price': str(desired_order['price']), 'side': order['side']})
                    
                    to_cancel.append(order)
                    logging.info("Amending the value of previous order")
        
        if buy_orders:
            while buys_matched < len(buy_orders):
                to_create.append(buy_orders[buys_matched])
                buys_matched += 1
        else:
            while sells_matched < len(sell_orders):
                to_create.append(sell_orders[sells_matched])
                sells_matched += 1

        print("to:create="+str(to_create))
        if to_create:
            logging.info("Creating %d orders:" % (len(to_create)))
            for order in reversed(to_create):
                logging.info("side = %d , amount =%s @ %s$" % (order['side'], order['amount'], order['price']))
            if settings.DEBUG:
                var = str(input("input 'Yes' for further process :"))
                if var == "Yes":
                    self.exchange.create_bulk_orders(to_create)
                else:
                    logging.info("cancelling order side = %s, amount = %s @ %s$" % (order['side'], order['amount'], order['price']))
            else:
                self.exchange.create_bulk_orders(to_create)
                

        # Could happen if we exceed a delta limit
        if len(to_cancel) > 0:
            logging.info("Canceling %d orders:" % (len(to_cancel)))
            for order in reversed(to_cancel):
                logging.info("id = %d side = %d amount = %s @ %s$" % (order['id'], order['side'], order['amount'], order['price']))
            if settings.DEBUG:
                var = str(input("input 'Yes' for further process :"))
                if var == "Yes":
                        response = self.exchange.cancel_bulk_orders(to_cancel)
                else:
                    logging.info("cancelling cancel order side = %s amount = %s @ %s$" % (order['side'], order['amount'], order['price']))
            else:
                self.exchange.cancel_bulk_orders(to_cancel)


    ###
    # Position Limits
    ###

    def short_position_limit_exceeded(self):
        """Returns True if the short position limit is exceeded"""
        if not settings.CHECK_POSITION_LIMITS:
            return False
        position = float(self.exchange.get_delta())
        return position <= settings.MIN_POSITION

    def long_position_limit_exceeded(self):
        """Returns True if the long position limit is exceeded"""
        if not settings.CHECK_POSITION_LIMITS:
            return False
        position = float(self.exchange.get_delta())
        return position >= settings.MAX_POSITION
    
    def check_usdt(self, price):
        position = float(self.exchange.get_position()['USDT']['available'])
        if price > position:
            return False
        return True

    ###
    # Sanity
    ##

    def perform_check(self):
        """Perform checks before placing orders."""

        # Check if OB is empty - if so, can't quote.
        # self.exchange.check_if_orderbook_empty()

        # # Ensure market is still open.
        # self.exchange.check_market_open()

        # Get ticker, which sets price offsets and prints some debugging info.
        # ticker = self.get_ticker()

        # Sanity check:
        # if self.get_price_offset(-1) >= ticker["sell"] or self.get_price_offset(1) <= ticker["buy"]:
        #     logging.error("Buy: %s, Sell: %s" % (self.start_position_buy, self.start_position_sell))
        #     logging.error("Sanity check failed, exchange data is inconsistent")
        #     self.exit()

        # Messaging if the position limits are reached
        if self.long_position_limit_exceeded():
            logging.warning("Long delta limit exceeded")
            logging.warning("Current Position: %.f, Maximum Position: %.f" %
                        (self.exchange.get_delta(), settings.MAX_POSITION))
            self.exit()

        if self.short_position_limit_exceeded():
            logging.warning("Short delta limit exceeded")
            logging.warning("Current Position: %.f, Minimum Position: %.f" %
                        (self.exchange.get_delta(), settings.MIN_POSITION))
            self.exit()
        
        if self.exchange.get_pending_orders().get('result').get('CTSUSDT').get('records') is not None:
            if len(self.exchange.get_pending_orders().get('result').get('CTSUSDT').get('records')) > settings.MAX_PENDING_ORDERS:
                logging.warning("Pending Order limit exceeded")

    ###########
    # Running #
    ###########

    def check_file_change(self):
        """Restart if any files we're watching have changed."""
        for f, mtime in watched_files_mtimes:
            if getmtime(f) > mtime:
                self.restart()


    def exit(self):
        logging.info("Shutting down. All open orders will be cancelled.")
        try:
            self.exchange.cancel_all_orders()
            # self.exchange.hotbit.exit()
        except AuthenticationError as e:
            logging.info("Was not authenticated; could not cancel orders.")
        except Exception as e:
            logging.info("Unable to cancel orders: %s" % e)

        sys.exit()

    def run_loop(self):
        while True:
            sys.stdout.write("-----\n")
            sys.stdout.flush()
            settings.get_input_range()
            self.check_file_change()
            sleep(settings.LOOP_INTERVAL)

            # This will restart on very short downtime, but if it's longer,
            # the MM will crash entirely as it is unable to connect to the WS on boot.
            if not self.check_connection():
                logging.error("Realtime data connection unexpectedly closed, restarting.")
                self.restart()

            self.perform_check()  # Ensures health of mm - several cut-out points here
            self.print_status()  # Print delta, etc
            self.place_orders()  # Creates desired orders and converges to existing orders

    def restart(self):
        logging.info("Restarting the market maker...")
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    def check_connection(self):
        return True if self.exchange.get_delta() else False




def run():
    logging.info('HotBit Market Maker')

    ordermanager = OrderManager()
    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        ordermanager.run_loop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
        
        
class AuthenticationError(Exception):
        pass

class MarketClosedError(Exception):
    pass

class MarketEmptyError(Exception):
    pass