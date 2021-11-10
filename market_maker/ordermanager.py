import datetime, sys, math, random
from market_maker import settings
from os.path import getmtime
from logger import logging
from market_maker.exchange_interface import ExchangeInterface


import os
# watched_files_mtimes = [(f, getmtime(f)) for f in settings.WATCHED_FILES]



class OrderManager:
    def __init__(self):
        self.exchange = ExchangeInterface()
        # O```````````````````````````nce exchange is created, register exit handler that will always cancel orders
        # on any error.

        logging.info("Using symbol %s." % self.exchange.symbol)

        logging.info("Order Manager initializing, connecting to BitMEX. Live run: executing real trades.")

        self.start_time = datetime.now()
        self.starting_qty = self.exchange.get_delta()
        self.running_qty = self.starting_qty
        self.reset()

    def reset(self):
        self.exchange.cancel_all_orders()
        self.print_status()

        # Create orders and converge.
        self.place_orders()

    def print_status(self):
        """Print the current MM status."""

        margin = self.exchange.get_margin()
        position = self.exchange.get_position()
        self.running_qty = self.exchange.get_delta()

        logging.info("Current Contract Position: %d" % self.running_qty)
        if settings.CHECK_POSITION_LIMITS:
            logging.info("Position limits: %d/%d" % (settings.MIN_POSITION, settings.MAX_POSITION))
       
        logging.info("Contracts Traded This Run: %d" % (self.running_qty - self.starting_qty))

    def get_price_offset(self, index):
        """Given an index (1, -1, 2, -2, etc.) return the price for that side of the book.
           Negative is a buy, positive is a sell."""
        # Maintain existing spreads for max profit
        ############### CHECK THIS OUT ###############
        if settings.BUY_AGGRESSIVELY:
            SPREAD = settings.MAX_SPREAD
        else:
            SPREAD = settings.MIN_SPREAD
        price = self.exchange.market_status(period=settings.LAST_VALUE_PERIOD)['result']['open']
        if settings.MAINTAIN_SPREADS:
            if self.get_highest_buy() > self.get_lowest_sell():
                prices = []
                for i in range(1, settings.MAX_ORDER_PAIRS):
                    prices.append(round(random.uniform(price, price+price*SPREAD/100), settings.PRICE_PRECISION))
                    
                    if prices[i] > self.get_highest_buy():
                        prices[i] = self.get_highest_buy() if settings.MAINTAIN_SPREAD else self.get_highest_buy() + self.get_highest_buy()*settings.SPREAD / 100
                    if price[i] < self.get_lowest_sell():
                        prices[i] = self.get_lowest_sell()
                    
                prices.sort()
            elif self.get_highest_buy() <= self.get_lowest_sell():
                prices = []
                for i in range(1, settings.MAX_ORDER_PAIRS):
                    # prices.append(round(random.uniform(price, price+price*SPREAD/100), settings.PRICE_PRECISION))
                    
                    # or
                    prices.append(round(self.get_lowest_sell + self.get_lowest_sell*SPREAD/100, settings.PRICE_PRECISION))
                    if prices[i] < self.get_lowest_sell():
                        prices[i] = round(self.get_lowest_sell + self.get_lowest_sell*SPREAD/100, settings.PRICE_PRECISION)

                prices.sort()
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
        result = self.exchange.market_status(period=1296000)['results']
        last_fortnight_value = result['open']
        recent_value = result['last']
        
        recent_orders = self.exchange.get_recent_orders()
        results = recent_orders['result']
        bid_amount = 0
        sell_amount = 0
        for result in results:
            if result['type'] == "buy":
                bid_amount += float(result['amount'])
            else:
                sell_amount += float(result['amount'])
        if bid_amount > sell_amount:
            print("buyer is greater than seller sell some volume")
            change = bid_amount - sell_amount
            index = 1 # 1 for selling
            buy_orders = self.prepare_order(index, amount=change)
        elif bid_amount < sell_amount:
            print("seller are grater than buyer, buy some volume..")
            change = sell_amount - bid_amount
            index = -1 # -1 for buying
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
        orderQty = amount / settings.MAX_ORDER_PAIRS if settings.BUY_AGGRESIVELY else amount - amount*settings.MAX_SPREAD / settings.MAX_ORDER_PAIRS
        orders = []
        # if settings.RANDOM_ORDER_SIZE is True:
        #     quantity = random.randint(settings.MIN_ORDER_SIZE, settings.MAX_ORDER_SIZE)
        # else:
        #     quantity = settings.ORDER_START_SIZE + ((abs(index) - 1) * settings.ORDER_STEP_SIZE)
        prices = self.get_price_offset(index, settings.MAX_ORDER_PAIRS)
        for i in range(1, settings.MAX_ORDER_PAIRS+1):
            
            orders.append({'price': prices[i], 'orderQty': amount, 'side': "buy" if index < 0 else "Sell"})

        
        print(orders)
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
        existing_user_orders = self.exchange.get_pending_orders()

        # Check all existing orders and match them up with what we want to place.
        # If there's an open one, we might be able to amend it to fit what we want.
        for order in existing_user_orders:
            try:
                if order['side'] == 'buy':
                    desired_order = buy_orders[buys_matched]
                    buys_matched += 1
                else:
                    desired_order = sell_orders[sells_matched]
                    sells_matched += 1

                # Found an existing order. Do we need to amend it?
                if desired_order['orderQty'] != order['volume'] or (
                        # If price has changed, and the change is more than our RELIST_INTERVAL, amend.
                        desired_order['price'] != order['price'] and
                        abs((desired_order['price'] / order['price']) - 1) > settings.RELIST_INTERVAL):
                    to_amend.append({'orderID': order['orderID'], 'orderQty': order['cumQty'] + desired_order['orderQty'],
                                     'price': desired_order['price'], 'side': order['side']})
            except Exception as e:
                # Will throw if there isn't a desired order to match. In that case, cancel it.
                print(e)
                to_cancel.append(order)

        while buys_matched < len(buy_orders):
            to_create.append(buy_orders[buys_matched])
            buys_matched += 1

        while sells_matched < len(sell_orders):
            to_create.append(sell_orders[sells_matched])
            sells_matched += 1

        if len(to_amend) > 0:
            for amended_order in reversed(to_amend):
                reference_order = [o for o in existing_orders if o['orderID'] == amended_order['orderID']][0]
                logging.info("Amending %4s: %d @ %.*f to %d @ %.*f (%+.*f)" % (
                    amended_order['side'],
                    reference_order['leavesQty'], tickLog, reference_order['price'],
                    (amended_order['orderQty'] - reference_order['cumQty']), tickLog, amended_order['price'],
                    tickLog, (amended_order['price'] - reference_order['price'])
                ))
            # This can fail if an order has closed in the time we were processing.
            # The API will send us `invalid ordStatus`, which means that the order's status (Filled/Canceled)
            # made it not amendable.
            # If that happens, we need to catch it and re-tick.
            try:
                self.exchange.amend_bulk_orders(to_amend)
            except requests.exceptions.HTTPError as e:
                errorObj = e.response.json()
                if errorObj['error']['message'] == 'Invalid ordStatus':
                    logging.warning("Amending failed. Waiting for order data to converge and retrying.")
                    sleep(0.5)
                    return self.place_orders()
                else:
                    logging.error("Unknown error on amend: %s. Exiting" % errorObj)
                    sys.exit(1)

        if len(to_create) > 0:
            logging.info("Creating %d orders:" % (len(to_create)))
            for order in reversed(to_create):
                logging.info("%4s %d @ %.*f" % (order['side'], order['orderQty'], tickLog, order['price']))
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
                logging.info("%4s %d @ %.*f" % (order['side'], order['leavesQty'], tickLog, order['price']))
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
        position = self.exchange.get_delta()
        return position <= settings.MIN_POSITION

    def long_position_limit_exceeded(self):
        """Returns True if the long position limit is exceeded"""
        if not settings.CHECK_POSITION_LIMITS:
            return False
        position = self.exchange.get_delta()
        return position >= settings.MAX_POSITION

    ###
    # Sanity
    ##

    def perform_check(self):
        """Perform checks before placing orders."""

        # Check if OB is empty - if so, can't quote.
        self.exchange.check_if_orderbook_empty()

        # Ensure market is still open.
        self.exchange.check_market_open()

        # Get ticker, which sets price offsets and prints some debugging info.
        # ticker = self.get_ticker()

        # Sanity check:
        if self.get_price_offset(-1) >= ticker["sell"] or self.get_price_offset(1) <= ticker["buy"]:
            logging.error("Buy: %s, Sell: %s" % (self.start_position_buy, self.start_position_sell))
            logging.error("First buy position: %s\nBitMEX Best Ask: %s\nFirst sell position: %s\nBitMEX Best Bid: %s" %
                         (self.get_price_offset(-1), ticker["sell"], self.get_price_offset(1), ticker["buy"]))
            logging.error("Sanity check failed, exchange data is inconsistent")
            self.exit()

        # Messaging if the position limits are reached
        if self.long_position_limit_exceeded():
            logging.info("Long delta limit exceeded")
            logging.info("Current Position: %.f, Maximum Position: %.f" %
                        (self.exchange.get_delta(), settings.MAX_POSITION))

        if self.short_position_limit_exceeded():
            logging.info("Short delta limit exceeded")
            logging.info("Current Position: %.f, Minimum Position: %.f" %
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




def run():
    logging.info('HotBit Market Maker')

    ordermanager = OrderManager()
    # Try/except just keeps ctrl-c from printing an ugly stacktrace
    try:
        ordermanager.run_loop()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()