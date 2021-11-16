import datetime, sys, math, random
from market_maker import settings
from .exchange_interface import ExchangeInterface
    
from os.path import getmtime
from logger import logging
from time import sleep


import os
watched_files_mtimes = [(f, getmtime(f)) for f in settings.WATCHED_FILES]



class OrderManager:
    def __init__(self):
        self.exchange = ExchangeInterface()
        # Once exchange is created, register exit handler that will always cancel orders
        # on any error.

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
        logging.info("highest bid = %f", self.get_highest_buy)
        logging.info("lowest sell = %f", self.get_lowest_sell)
        
        self.reset()

    def reset(self):
        self.exchange.cancel_all_orders()
        self.print_status()

        # Create orders and converge.
        self.place_orders()

    def print_status(self):
        """Print the current MM status."""

        margin = self.exchange.get_delta()
        position = self.exchange.get_position()
        self.running_qty = float(self.exchange.get_delta())

        # logging.info("Current Contract Position: %d" % self.running_qty)
        if settings.CHECK_POSITION_LIMITS:
            logging.info("Position limits: %d/%d" % (settings.MIN_POSITION, settings.MAX_POSITION))
       
        logging.info("Contracts Traded This Run: %d" % (self.running_qty - self.starting_qty))

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
        price = float(self.exchange.market_status(period=settings.LAST_VALUE_PERIOD)['result']['open'])
        if settings.MAINTAIN_SPREAD:
            if self.get_highest_buy > self.get_lowest_sell:
                
                for i in range(0, order_pairs):
                    prices.append(round(random.uniform(price, price+price*SPREAD/100), settings.PRICE_PRECISION))
                    
                    if prices[i] > self.get_highest_buy:
                        prices[i] = self.get_highest_buy if settings.MAINTAIN_SPREAD else self.get_highest_buy + self.get_highest_buy*settings.SPREAD / 100
                    if price[i] < self.get_lowest_sell:
                        prices[i] = self.get_lowest_sell
                    
                prices.sort()
            elif self.get_highest_buy <= self.get_lowest_sell:
                for i in range(0, order_pairs):
                    # prices.append(round(random.uniform(price, price+price*SPREAD/100), settings.PRICE_PRECISION))
                    
                    # or
                    prices.append(round(random.uniform(self.get_lowest_sell, self.get_lowest_sell + self.get_lowest_sell*SPREAD/100), settings.PRICE_PRECISION))
                    if prices[i] < self.get_lowest_sell:
                        prices[i] = round(random.uniform(self.get_lowest_sell, self.get_lowest_sell + self.get_lowest_sell*SPREAD/100), settings.PRICE_PRECISION)

                prices.sort()
            
        else:
            pass
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
        period = 1296000
        result = self.exchange.market_status(period=1296000)
        last_fortnight_value = float(result['result']['open'])
        recent_value = float(result['result']['last'])
        previous_value =  float(self.exchange.market_status(period=settings.LAST_VALUE_PERIOD)['result']['last'])
        
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
        if abs(bid_amount - sell_amount)*100 / min(bid_amount, sell_amount) > settings.FLUCTUATION:
            if bid_amount > sell_amount or (previous_value < recent_value):
                print("buyer is greater than seller sell some volume")
                change = bid_amount - sell_amount
                index = 1 # 1 for selling
                buy_orders = self.prepare_order(index, amount=change)
            elif bid_amount < sell_amount or (previous_value > recent_value):
                print("seller are grater than buyer, buy some volume..")
                change = sell_amount - bid_amount
                index = 2 # -1 for buying
                sell_orders = self.prepare_order(index, amount=change)
            
            else:
                # if settings.BUY_AGGRESIVELY:
                #     if (last_fortnight_value - recent_value)*100/last_fortnight_value > settings.PERCENTAGE_CHANGE_FORTNIGHT
                #         index = -1 # -1 for buying
                #         print("buyer are equal to seller, buying aggresively")
                # buy_orders.append(self.prepare_order(index, amount=settings.BUY_AGGRESSIVE_COUNT))
                # if (recent_value - last_fortnight_value)*100/last_fortnight_value > settings.PERCENTAGE_CHANGE_FORTNIGHT
                #         index = 1 # 1 for selling
                #         print("buyer are equal to seller, buying aggresively")
                # buy_orders.append(self.prepare_order(index, amount=settings.BUY_AGGRESSIVE_COUNT))
                # else:
                print("SELLER ARE EQUAL TO BUYER.. NOTHING TO DO")
                

        return self.converge_orders(buy_orders, sell_orders)

    def prepare_order(self, index, amount):
        """Create an order object."""
        orderQty = (amount / settings.MAX_ORDER_PAIRS) 
        orders = []
        # if settings.RANDOM_ORDER_SIZE is True:
        #     quantity = random.randint(settings.MIN_ORDER_SIZE, settings.MAX_ORDER_SIZE)
        # else:
        #     quantity = settings.ORDER_START_SIZE + ((abs(index) - 1) * settings.ORDER_STEP_SIZE)
        prices = self.get_price_offset(index, settings.MAX_ORDER_PAIRS)
        for i in range(0, settings.MAX_ORDER_PAIRS):
            
            orders.append({'price': prices[i], 'orderQty': orderQty, 'side': index})

        print(orders)
        return orders

    def converge_orders(self, buy_orders, sell_orders):
        """Converge the orders we currently have in the book with what we want to be in the book.
           This involves amending any open orders and creating new ones if any have filled completely.
           We start from the closest orders outward."""

        # tickLog = self.exchange.get_instrument()['tickLog']
        to_amend = []
        repeated_order = []
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
        if len(existing_user_orders):
            for order in existing_user_orders:
                
                desired_order = None
                if order['side'] == 1 or order['side'] == '1':   # 1-Seller，2-buyer
                    # for seller
                    if len(sell_orders):
                        desired_order = sell_orders[sells_matched]
                        sells_matched +=1
                    else:
                        logging.info("previously sell orders were placed now buy orders are being placed")
                        
                if order['side'] == 2 or order['side'] == '2':   # 1-Seller，2-buyer
                    # for buyer
                    if len(buy_orders):
                        desired_order = buy_orders[sells_matched]
                        buys_matched +=1
                    else:
                        logging.info("previously sell orders were placed now buy orders are being placed")
                        
                if desired_order['amount'] != order['left'] or (abs((desired_order['price'] / order['price']) - 1) > settings.RELIST_INTERVAL):
                    to_amend.append({'id': order['id'], 'amount': order['left'] + desired_order['amount'],
                                        'price': desired_order['price'], 'side': order['side']})
                    
                    to_cancel.append(order)
        else:
            to_create.append(buy_orders if buy_orders else sell_orders)
        
        if to_create is []:
            while buys_matched < len(buy_orders):
                to_create.append(buy_orders[buys_matched])
                buys_matched += 1

            while sells_matched < len(sell_orders):
                to_create.append(sell_orders[sells_matched])
                sells_matched += 1
                
            if len(buy_orders) or len(sell_orders):
                for o in to_amend:
                    to_create.append(o)

        if len(to_create) > 0:
            logging.info("Creating %d orders:" % (len(to_create)))
            for order in reversed(to_create):
                logging.info("%d %d @ %d" % (order['side'], order['amount'], order['price']))
                if settings.DEBUG:
                    var = str(input("input 'Yes' for further process :"))
                    if var == "Yes":
                        self.exchange.create_bulk_orders(to_create)
                    else:
                        logging.info("cancelling order %4s %d @ %.*f" % (order['side'], order['orderQty'], order['price']))
                else:
                    self.exchange.create_bulk_orders(to_create)

        # Could happen if we exceed a delta limit
        if len(to_cancel) > 0:
            logging.info("Canceling %d orders:" % (len(to_cancel)))
            for order in reversed(to_cancel):
                logging.info("%d %d @ %d" % (order['side'], order['amount'], order['price']))
            if settings.DEBUG:
                var = str(input("input 'Yes' for further process :"))
                if var == "Yes":
                        self.exchange.cancel_bulk_orders(to_cancel)
                else:
                    logging.info("cancelling cancel order %4s %d @ %.*f" % (order['side'], order['orderQty'], order['price']))
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
        #     logging.error("First buy position: %s\nBitMEX Best Ask: %s\nFirst sell position: %s\nBitMEX Best Bid: %s" %
        #                  (self.get_price_offset(-1), ticker["sell"], self.get_price_offset(1), ticker["buy"]))
        #     logging.error("Sanity check failed, exchange data is inconsistent")
        #     self.exit()

        # Messaging if the position limits are reached
        if self.long_position_limit_exceeded():
            logging.warning("Long delta limit exceeded")
            logging.warning("Current Position: %.f, Maximum Position: %.f" %
                        (self.exchange.get_delta(), settings.MAX_POSITION))

        if self.short_position_limit_exceeded():
            logging.warning("Short delta limit exceeded")
            logging.warning("Current Position: %.f, Minimum Position: %.f" %
                        (self.exchange.get_delta(), settings.MIN_POSITION))

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
            self.exchange.bitmex.exit()
        except errors.AuthenticationError as e:
            logging.info("Was not authenticated; could not cancel orders.")
        except Exception as e:
            logging.info("Unable to cancel orders: %s" % e)

        sys.exit()

    def run_loop(self):
        while True:
            sys.stdout.write("-----\n")
            sys.stdout.flush()

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
        return True if len(self.exchange.get_position()) is not None else False




def run():
    logging.info('HotBit Market Maker')

    ordermanager = OrderManager()
    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        ordermanager.run_loop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()