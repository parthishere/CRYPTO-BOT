import requests
from pathlib import Path
import dotenv, hashlib, os, datetime, time

import settings

SERVER_TIME = "https://api.hotbit.io/api/v1/server.time"
BALANCE_QUERY = "https://api.hotbit.io/api/v1/balance.query"
BALANCE_HISTORY = "https://api.hotbit.io/api/v1/balance.history"

ORDER_PUT_LIMIT = "https://api.hotbit.io/api/v1/order.put_limit" # Limit Order Transaction
ORDER_CANCEL = "https://api.hotbit.io/api/v1/order.cancel" # Cancel Transaction
ORDER_BULK_CANCEL = "https://api.hotbit.io/api/v1/order.batch_cancel" # Cancel transactions in large quantities
ORDER_DEALS = "https://api.hotbit.io/api/v1/order.deals" # Obtain the details of settled orders
ORDER_FINISHED_DETAIL = "https://api.hotbit.io/api/v1/order.finished_detail" # Check finished orders according to order number
ORDER_BOOK = "https://api.hotbit.io/api/v1/order.book" # Have to add parameters see doc! # obtain list of transaction
ORDER_PENDING = "https://api.hotbit.io/api/v1/order.pending" # CHECK UNEXECUTED ORDERS

MARKET_LIST = "https://api.hotbit.io/api/v1/market.list" # Obtain the list of transaction pairs
MARKET_LAST = "https://api.hotbit.io/api/v1/market.last" # have to add paramer # obtain the latest price of designated transaction pair
MARKET_DEALS = "https://api.hotbit.io/api/v1/market.deals" # orderbook
MARKET_KLINE = "https://api.hotbit.io/api/v1/market.kline" # Parameters required # Check K Chart
MARKET_STATUS = "https://api.hotbit.io/api/v1/market.status" # obtain the latest status of the market during the designated period of time in the past,l such as latest range of increase and decline, trading volume, highest/lowest price etc. # para required
MARKET_24_HR = "https://api.hotbit.io/api/v1/market.status24h" # obtain today's market status 
MARKET_SUMMERY = "https://api.hotbit.io/api/v1/market.summary" # market summary

ALLTICKER = "https://api.hotbit.io/api/v1/allticker" # obtain the latest trading informnation of all transaction pairs in the market

HEADERS = {'Content-type': 'application/x-www-form-urlencoded'}


class Hotbit:
    def __init__(self, api_key, secret_key, symbol):
        self.BASE_DIR = Path(__file__).resolve().parent
        dotenv_file = os.path.join(self.BASE_DIR, ".env")
        if os.path.isfile(dotenv_file):
            dotenv.load_dotenv(dotenv_file)

        hashlib.md5().digest()
        SIGN = hashlib.md5()

        self.SECRET_KEY = secret_key if secret_key is not None else os.environ['secret_key']
        self.API_KEY = api_key if api_key is not None else os.environ['api_key']
        self.SYMBOL = symbol if symbol is not None else os.environ['symbol']

        RAW = str("api_key={}&assets={}&secret_key={}".format(self.API_KEY, self.SYMBOL, self.SECRET_KEY))
        SIGN.update(RAW.encode('utf-8'))
        SIGN.digest()

        self.SIGN = str(SIGN.hexdigest()).upper()
        
        if symbol is None:
            self.symbol = settings.symbol
            self.market = settings.market
            self.market = settings.market
            self.symbol = settings.symbol
            
        self.symbol = settings.symbol
        self.market = settings.market
        self.markets = settings.markets
        self.symbol = settings.symbol

    def get_server_time():
        return requests.get(SERVER_TIME).json()

    def get_epoch_time(object):
        year = object.year
        month = 0
        day = 0
        hours = 0
        seconds = 0
        epoch_time = datetime.datetime(year, month, day, hours, seconds).timestamp()
        return epoch_time

    def get_epoch_now():
        epoch_time = datetime.datetime(time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday, time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec).timestamp()
        return epoch_time
    
    
    ############
    ## MARKET ##
    ############
    
    def market_summery(self, markets=None):
        if markets is None:
            markets=self.markets
        response = requests.get("{}?markets={}".format(MARKET_SUMMERY, markets), headers=HEADERS)
        return response.json()
  

    def market_kline(self, start_time=0, end_time=0, interval=settings.INTERVAL, market=None):
        if market is None:
            market=self.market
        response = requests.get("{}?market={}&start_time={}&end_time={}&interval={}".format(MARKET_KLINE, market, start_time, end_time, interval), headers=HEADERS) 
        return response.json()
    

    def all_tiker(self):
        response = requests.get(ALLTICKER, headers=HEADERS)
        return response.json()

    #############
    ## ACCOUNT ##
    #############
    
    def get_account_status(self):
        pass
    
    def get_balance_history(self, business, start_time, end_time, offset, limit):
        '''
        | Name of Method | Type of Method | Description |
        | balance.history | post  | Obtain the records regarding the changes in user assets |
        '''
        if not business:
            business="deposit"
        parameter_for_history = "api_key={}&sign={}&asset={}&business={}&start_time={}&end_time={}&offset={}&limit={}".format(settings.API_KEY, settings.SIGN, settings.ASSET, business, start_time, end_time, offset, limit)
        response = requests.post(BALANCE_HISTORY, data=parameter_for_history )
        return response.json()

    def get_balance_query(self):
        '''
        | Name of Method | Type of Method | Description |
        | balance.query | post  | Obtain User Assets |  
        '''
        assets = ['CTS', 'ETH', 'BTC']
        parameter = 'api_key=34e2bb5d-2047-8ab1-67395b7934a798c3&assets=["CTS"]&sign=84EB6F6B2E85D76C9864CBA62ADB806B'
        response = requests.post(BALANCE_QUERY, data=parameter)
        return response.json()

    def check_market_open(self):
        resopose = requests.get()
    
    def sell(self, amount=0, price=0):
        side = 1 # 1 for sell and 2 for buy
        params = "api_key={}&sign={}&market={}&side={}&amount={}&price={}&isfee={}".format(settings.API_KEY, settings.SIGN, side, amount, price, settings.ISFEE)
        response = requests.post(ORDER_PUT_LIMIT, data=params)
    
    def buy(self, amount=0, price=0):
        side = 2 # 1 for sell and 2 for buy
        if self.get_balance_query().get('result').get('CTS').get('available') < price*amount:
            print("dont have enough credit")
        params = "api_key={}&sign={}&market={}&side={}&amount={}&price={}&isfee={}".format(settings.API_KEY, settings.SIGN, side, amount, price, settings.ISFEE)
        response = requests.post(ORDER_PUT_LIMIT, data=params)
    
    def order_cancel(self, order_id=0):
        params = "api_key={}&sign={}&market={}&order_id={}".format(settings.API_KEY, settings.SIGN, settings.MARKET, order_id)
        response = requests.post(ORDER_CANCEL, data=params)

    def bulk_cancel(self, orders_id=[0]):
        params = "api_key={}&sign={}&market={}&orders_id={}".format(settings.API_KEY, settings.SIGN, settings.MARKET, orders_id)
        response = requests.post(ORDER_BULK_CANCEL, data=params)

    def order_detail(self, order_id=0, offset=settings.OFFSET):
        params = "api_key={}&sign={}&market={}&order_id={}".format(settings.API_KEY, settings.SIGN, settings.MARKET, order_id)
        response = requests.post(ORDER_DEALS, data=params)
        
    def order_depth(self, market='CTS/USDT', limit=100, interval='1e-8'):
        response = requests.get("https://api.hotbit.io/api/v1/order.depth?market={}&limit={}&interval={}".format(market, limit, interval))
        return response.json()
    
    def order_status(self, order_id):
        if requests.post("https://api.hotbit.io/api/v1/order.finished_detail"):
            return "Finished"
        if requests.post("https://api.hotbit.io/api/v1/order.pending"):
            return "Pending"
    
    def check_pending_orders(self,  offset=settings.OFFSET, limit=settings.LIMIT):
        params = "api_key={}&sign={}&market={}&offset={}&limit={}".format(settings.API_KEY, settings.SIGN, settings.MARKET, offset, limit)
        response = requests.post(ORDER_PENDING, data=params)
        
    def order_finished(self, start_time, end_time, offset, limit, side):
        params = "api_key={}&sign={}&market={}&start_time={}&end_time={}&offset={}&limit={}&side={}".format(settings.API_KEY, settings.SIGN, settings.MARKET, start_time, end_time, offset, limit, side)
        reponse = requests.post(ORDER_FINISHED_DETAIL, data=params)
    

    def get_crypto_price(self, market=None):    
        CRYPTO_CURRENT_VALUE = float(requests.get("https://api.hotbit.io/api/v1/market.last?market=CTS/USDT", data=PARAMS).json().get('result'))
 
    