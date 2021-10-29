import requests, hashlib, datetime, time, dotenv, os, mysql.connector, logger, datetime
from pathlib import Path
from pprint import pprint
import settings

try:
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="1234")
except:
    pass



    def print_status(self):
        """Print the current MM status."""

        margin = self.exchange.get_margin()
        position = self.exchange.get_position()
        self.running_qty = self.exchange.get_delta()
        tickLog = self.exchange.get_instrument()['tickLog']
        self.start_XBt = margin["marginBalance"]

        logger.info("Current XBT Balance: %.6f" % XBt_to_XBT(self.start_XBt))
        logger.info("Current Contract Position: %d" % self.running_qty)
        if settings.CHECK_POSITION_LIMITS:
            logger.info("Position limits: %d/%d" % (settings.MIN_POSITION, settings.MAX_POSITION))
        if position['currentQty'] != 0:
            logger.info("Avg Cost Price: %.*f" % (tickLog, float(position['avgCostPrice'])))
            logger.info("Avg Entry Price: %.*f" % (tickLog, float(position['avgEntryPrice'])))
        logger.info("Contracts Traded This Run: %d" % (self.running_qty - self.starting_qty))
        logger.info("Total Contract Delta: %.4f XBT" % self.exchange.calc_delta()['spot'])




 






def get_input_range(lower_range=settings.INPUT_UPPER_RANGE, upper_range=settings.INPUT_UPPER_RANGE):
    global INPUT_LOWER_RANGE, INPUT_UPPER_RANGE
    INPUT_UPPER_RANGE = upper_range
    INPUT_LOWER_RANGE = lower_range
    CRYPTO_CURRENT_VALUE = float(requests.get("https://api.hotbit.io/api/v1/market.last?market=CTS/USDT", data=PARAMS).json().get('result'))
    if CRYPTO_CURRENT_VALUE < INPUT_LOWER_RANGE or CRYPTO_CURRENT_VALUE > INPUT_UPPER_RANGE:
        raise Exception("Range should be bounded to crypto current value")



# response = requests.get("{}?market=CTS/USDT".format(MARKET_LAST), data=PARAMS)
# print(response)

# print(response.content)
# print(response.text)
# print(response.json())




# print(CRYPTO_CURRENT_VALUE)


class Difference():
    
    def __init__(self, USDT_DICT=None, BTC_DICT=None):
        self.usd_ask_volume = USDT_DICT["ask_amount"]
        self.btc_ask_volume = BTC_DICT["ask_amount"]
        
        self.usd_bid_volume = USDT_DICT["bid_amount"]
        self.btc_bid_volume = BTC_DICT["bid_amount"]
        
        self.total_ask_amount = self.usd_ask_volume + self.btc_ask_volume
        self.total_bid_amount = self.usd_bid_volume + self.btc_bid_volume
        

    

    
    
# # time ,open, close, high, low ,volume, deal, market  
# response = requests.get("https://api.hotbit.io/api/v1/market.kline?market=CTS/USDT&start_time=1634887815&end_time=1634887841&interval=60")
# print(response.content)

# # all the data about CTS
# response = requests.get("https://api.hotbit.io/api/v1/market.status?market=CTS/USDT&period=10")
# print(response.content)


# #A account status of user
# response = requests.post("https://api.hotbit.io/api/v1/balance.query", data=PARAMS2)
# print(response.content)



# if __name__ == '__main__':
#     market = Market()
#     account= Account()
#     order = Order()
    
#     print(CRYPTO_CURRENT_VALUE)
    
#     orders_depth = order.order_depth()

#     asks = orders_depth['result']['asks']
#     bids = orders_depth['result']['asks']

#     for volume, price in asks:
#         final_ask_volume += float(volume)
        
#     for volume, price in bids:
#         final_bid_volume += float(volume)
        
#     market_summery = market.market_summery()
#     market_summery_cts_btc = None
#     market_summery_cts_usdt = None
#     for market in market_summery["result"]:
#         if (market["name"] == "CTSUSDT"):
#             market_summery_cts_usdt = market
#         if  (market["name"] == "CTSBTC"):
#             market_summery_cts_btc = market
#     print(market_summery_cts_usdt['ask_amount'], market_summery_cts_btc['ask_amount'])
#     print(market_summery_cts_usdt['bid_amount'], market_summery_cts_btc['bid_amount'])
#     diff = Difference(market_summery_cts_usdt, market_summery_cts_btc)
    



# ask = seller
# bid = buyer