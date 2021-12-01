import requests
from pathlib import Path
import dotenv, hashlib, os, datetime, time

from market_maker import settings

SERVER_TIME = "https://api.hotbit.io/api/v1/server.time"
BALANCE_QUERY = "https://api.hotbit.io/api/v1/balance.query"
BALANCE_HISTORY = "https://api.hotbit.io/v2/p2/balance.history"

ORDER_PUT_LIMIT = "https://api.hotbit.io/v2/p2/order.put_limit" # Limit Order Transaction
ORDER_CANCEL = "https://api.hotbit.io/api/v1/order.cancel" # Cancel Transaction
ORDER_BULK_CANCEL = "https://api.hotbit.io/v2/p2/order.batch_cancel" # Cancel transactions in large quantities
ORDER_DEALS = "https://api.hotbit.io/api/v1/order.deals" # Obtain the details of settled orders
ORDER_FINISHED_DETAIL = "https://api.hotbit.io/api/v1/order.finished_detail" # Check finished orders according to order number
ORDER_FINISHED_LIST = "https://api.hotbit.io/api/v1/order.finished"
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


import logging
logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')


class Hotbit():
    def __init__(self, api_key=None, secret_key=None, symbol=None):

        self.SECRET_KEY = secret_key if secret_key is not None else os.environ['secret_key']
        self.API_KEY = api_key if api_key is not None else os.environ['api_key']
        self.SYMBOL = symbol if symbol is not None else os.environ['assets']
        
        # if symbol is None:
        #     self.symbol = settings.symbol
        #     self.market = settings.market
        #     self.market = settings.market
            
        self.symbol = settings.ASSETS
        self.market = settings.MARKET

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
    
    def get_trade_history(self, market=None, limit=1000):
        """
        {"error":null,
        "result":[{"id":3219750640,"time":1635931109,"price":"0.07278929","amount":"0.192","type":"sell"},
        {"id":3219749145,"time":1635931093,"price":"0.07278927","amount":"0.408","type":"buy"},
        {"id":3219739811,"time":1635930998,"price":"0.07278927","amount":"0.205","type":"buy"}],
        "id":104403852}
        """
        if market is None:
            market = settings.MARKET
        response = requests.get("{}?market={}&limit={}&last_id=400".format(MARKET_DEALS, market, limit)).json()
        return response
    
    def market_status(self, period=10, market=None):
        """
        Response:
        {
            "error": null,
            "result": {
                "period": 10,
                "last": "0.0743",
                "open": "0.074162",
                "close": "0.0743",
                "high": "0.0743",
                "low": "0.074162",
                "volume": "0.314",
                "deal": "0.023315531"
            },
            "id": 1521169247
        }
        """
        if not market:
            market = settings.MARKET
        response = requests.get("{}?market={}&period={}".format(MARKET_STATUS, market, period))
        return response.json()
        
    def market_summery(self, markets=None):
        """ 
        Response:
        {
            "error": null,
            "result": [
                {
                    "name": "ETHBTC",
                    "ask_count": 0,
                    "ask_amount": "0",
                    "bid_count": 0,
                    "bid_amount": "0"
                },
            ],
            "id": 1521169429
        }
        """
        if markets is None:
            markets=self.markets
        response = requests.get("{}?markets={}".format(MARKET_SUMMERY, markets), headers=HEADERS)
        return response.json()
  

    def market_kline(self, start_time=0, end_time=0, interval=settings.INTERVAL, market=None):
        """
        Response:
        {
            "error": null,
            "result": [   
            [1525067600, "11714.04", "11710.01", "11778.69", "11697.18", "13.604065", "159329.23062211", "BTCUSDT"], 
            [1565067660, "11703.47", "11716.65", "11720.55", "11703.47", "14.401973", "168649.82127032", "BTCUSDT"], 
            [1565067720, "11714.24", "11715.09", "11724.5", "11707.78", "12.287975", "143952.77384769", "BTCUSDT"]],#time ,open, close, high, low ,volume, deal, market
            "id": 1521169586
        }
        """
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
    
    def authentication_required(fn):
        """Annotation for methods that require auth."""
        def wrapped(self, *args, **kwargs):
            if not (self.API_KEY):
                msg = "You must be authenticated to use this method"
                raise AuthenticationError(msg)
            else:
                return fn(self, *args, **kwargs)
        return wrapped
    
    def get_account_status(self):
        pass
    
    @authentication_required
    def get_balance_history(self, business=None, start_time=0, end_time=int(round(get_epoch_now(), 0)), offset=0, limit=1000, asset=settings.ASSET):
        '''
        
        '''
        if not business:
            business="deposit"
        else:
            if not (business == "trade" or business == "deposit"):
                business="deposit"
            
                
        sign = self.get_sign_two(api_key=settings.API_KEY, assets=asset, business=business, start_time=start_time, end_time=end_time, offset=offset, limit=limit)
        parameter_for_history = "api_key={}&sign={}&asset={}&business={}&start_time={}&end_time={}&offset={}&limit={}".format(settings.API_KEY, sign, asset, business, start_time, end_time, offset, limit)
        response = requests.post(BALANCE_HISTORY, data=parameter_for_history)
        return response.json()

    @authentication_required
    def get_balance_query(self, assets=None):
        '''
        {'error': None,
        'result':
            {'CTS': {'available': '21285.43',
                'freeze': '0'}
            },
        'id': 19523998})  
        '''
        if assets == None:
            assets = []
        sign = self.get_sign(api_key=settings.API_KEY, assets=assets, secret_key=settings.SECRET_KEY)
        parameter = str(f'api_key={settings.API_KEY}&assets={assets}&sign={sign}')
        response = requests.post(BALANCE_QUERY, data=parameter, headers=HEADERS)
        return response.json()

    def check_market_open(self):
        resopose = requests.get()
    
    ###########
    ## ORDER ##
    ###########
    
    
    def get_recent_order_bids(self, market=settings.MARKET, limit=1000):
        """ 
        {"error":null,"result":{"limit":100,"offset":0,"total":62,"orders":[{"id":65026846809,"market":"ETHBTC","type":1,"side":1,"ctime":1636410981.387057,"mtime":1636410981.387057,"price":"0.07223","amount":"0.01","left":"0.01","deal_stock":"0","deal_money":"0","status":0},{"id":65008690302,"market":"ETHBTC","type":1,"side":1,"ctime":1636400949.443757,"mtime":1636400949.443757,"price":"0.07230001","amount":"0.003","left":"0.003","deal_stock":"0","deal_money":"0","status":0},
        """
        side = 2  # for buy
        response = requests.get("{}?market={}&side=2&offset=0&limit={}".format(ORDER_BOOK, market, limit)).json()
        return response
     
    def get_recent_order_sells(self, market=settings.MARKET, limit=1000):
        """ 
        {"error":null,"result":{"limit":100,"offset":0,"total":62,"orders":[{"id":65026846809,"market":"ETHBTC","type":1,"side":1,"ctime":1636410981.387057,"mtime":1636410981.387057,"price":"0.07223","amount":"0.01","left":"0.01","deal_stock":"0","deal_money":"0","status":0},{"id":65008690302,"market":"ETHBTC","type":1,"side":1,"ctime":1636400949.443757,"mtime":1636400949.443757,"price":"0.07230001","amount":"0.003","left":"0.003","deal_stock":"0","deal_money":"0","status":0},
        """   
        side = 1  # for sell
        response = requests.get("{}?market={}&side=1&offset=0&limit={}".format(ORDER_BOOK, market, limit)).json()
        return response
        
    
    def place_order(self, quantity, price, buy, sell):
        if price < 0:
            raise Exception("Price must be positive.")
        buy_orders = []
        sell_orders = []
    
    @authentication_required    
    def sell(self, amount=0, price=0, market=settings.MARKET, isfee=settings.ISFEE):
        """
        Response:
        {
            "error": null,
            "result": 
            {
            "id":8688803,    #order-ID
                "market":"ETHBTC",
                "source":"web",    #The source identification of data request
                "type":1,	       #Type of order pladement 1-limit order
                "side":2,	       #Identification of buyers and sellers 1-Seller，2-buyer
                "user":15731,
                "ctime":1526971722.164765, #Time of order establishment(second)
                "mtime":1526971722.164765, #Time of order update(second)
                "price":"0.080003",
                "amount":"0.4",
                "taker_fee":"0.0025",
                "maker_fee":"0",
                "left":"0.4",
                "deal_stock":"0",
                "deal_money":"0",
                "deal_fee":"0",
                "status":0    , #Sign of order status when 0x8 is true, it means the current order is cancelled, when 0x80 is true, it means that the current order is deducted by deductable tokens	    "fee_stock":"HTB",	#Name of deductable token
                "alt_fee":"0.5",	#The discount of deductable tokens
                "deal_fee_alt":"0.123" #Amount deducted
                },
            "id": 1521169460
        }
        """
        side = 1 # 1 for sell and 2 for buy
            
        sign_string = "amount=" + str(amount) + "&api_key=" + str(settings.API_KEY) +  "&isfee=0&market=" +  str(market) +  "&price=" + str(price) + "&side=" + str(side) + "&secret_key=" + str(settings.SECRET_KEY)

        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
        sign = sign.upper()
        
        body = {
            "api_key" : str(settings.API_KEY), 
            "amount" : amount,
            "isfee" : 0 ,
            "market" :   str(market),
            "price" : price,
            "side" : side,
            "sign": str(sign)   }
        
        response = requests.post(ORDER_PUT_LIMIT, data=body, headers=HEADERS).json()
        print(response)
        return response
    
    
    @authentication_required
    def buy(self, amount=0, price=0, market=settings.MARKET, isfee=settings.ISFEE):
        side = 2 # 1 for sell and 2 for buy
        
        sign_string = "amount=" + str(amount) + "&api_key=" + str(settings.API_KEY) +  "&isfee=0&market=" +  str(market) +  "&price=" + str(price) + "&side=" + str(side) + "&secret_key=" + str(settings.SECRET_KEY)

        sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
        sign = sign.upper()
        
        body = {
            "api_key" : str(settings.API_KEY), 
            "amount" : amount,
            "isfee" : 0 ,
            "market" :   str(market),
            "price" : price,
            "side" : side,
            "sign": str(sign)   }
        params = dict(api_key=settings.API_KEY, sign=sign, market=market, side=2, amount=amount, price=price, isfee=isfee)
        response = requests.post(ORDER_PUT_LIMIT, data=body, headers=HEADERS).json()
        print(response)
        return response
    
    
    @authentication_required
    def order_cancel(self, market=settings.MARKET, order_id=0):
        """
        {
            "error": null,
            "result": 
            {
            "id":8688803,    #order-ID
                "market":"ETHBTC",
                "source":"web",    #The source identification of data request
                "type":1,	       #Type of order pladement 1-limit order
                "side":2,	       #The sign of buyer and seller 1-seller，2-buyer
                "user":15731,
                "ctime":1526971722.164765, #Time of order establishment(second)
                "mtime":1526971722.164765, #Time of order update(second)
                "price":"0.080003",
                "amount":"0.4",
                "taker_fee":"0.0025",
                "maker_fee":"0",
                "left":"0.4",
                "deal_stock":"0",
                "deal_money":"0",
                "deal_fee":"0",
                "status":0    , #Sign of order status  when 0x8 is true, it means the current order is cancelled, when 0x80 is true, it means that the current order is deducted by deductable tokens	    "fee_stock":"HTB",	#Name of deductable token
                "alt_fee":"0.5",	#The discount of deductable tokens
                "deal_fee_alt":"0.123" #The amount deducted
                },
            "id": 1521169460
        }
        """
        sign = self.get_sign(api_key=settings.API_KEY, market=market, order_id=order_id, secret_key=settings.SECRET_KEY)
        params = "api_key={}&sign={}&market={}&order_id={}".format(settings.API_KEY, sign, settings.MARKET, order_id)
        response = requests.post(ORDER_CANCEL, data=params).json()
        return response
    
    @authentication_required
    def bulk_cancel(self, orders_id=None, market=settings.MARKET):
        """
        Response:
        {
            "error": null,
            "result": 
            [
                    {#Correct feedback
                        "id":8688803,    #order-ID(unsigned 64bit)
                            "market":"ETHBTC",
                            "source":"web",    #The source identification of data request
                            "type":1,	       #Type of order placement 1-limit order
                            "side":2,	       #sign of buyer and seller 1-seller，2-buyer
                            "user":15731,
                            "ctime":1526971722.164765, #Time of order establishment(second)
                            "mtime":1526971722.164765, #Time of order update(second)
                            "price":"0.080003",
                            "amount":"0.4",
                            "taker_fee":"0.0025",
                            "maker_fee":"0",
                            "left":"0.4",
                            "deal_stock":"0",
                            "deal_money":"0",
                            "deal_fee":"0",
                    "status":0    , #Sign of order status  when 0x8 is true, it means the current order is cancelled, when 0x80 is true, it means that the current order is deducted by deductable tokens		    "fee_stock":"HTB",	#Name of deductable token
                    "alt_fee":"0.5",	#The discount of deductable token
                        "deal_fee_alt":"0.123" #The amount deducted
                    },
                    {	#Error feedback occured
                        "error": {	
                "code":10
                "message":"order not found"
                }
                "result":null,
                    "id": 1521169460
                    }
                ],
            "id": 1521169460
        }

        """
        if not orders_id:
            orders_id = []
        sign = self.get_sign_two(api_key=settings.API_KEY, market=market, orders_id=orders_id)
        params = "api_key={}&sign={}&market={}&orders_id={}".format(settings.API_KEY, sign, settings.MARKET, orders_id)
        response = requests.post(ORDER_BULK_CANCEL, data=params).json()
        return response

    @authentication_required
    def order_detail(self, limit=1000, order_id=None):
        """
        Response:
        {
            "error": null,
            "result": {
                "offset": 10,
                "limit": 10,
                "records": [
                    {
                        "time": 1521107411.116817,
                        "user": 15643,
                        "id": 1385154,
                        "role": 1,
                        "price": "0.02",
                        "amount": "0.071",
                        "deal": "0.00142",
                        "fee": "0",
                        "deal_order_id": 2337658
                    },
                    {
                        "time": 1521107410.357024,#(秒)
                        "user": 15643,
                        "id": 1385151,
                        "role": 1,7
                        "price": "0.02",
                        "amount": "0.081",
                        "deal": "0.00162",
                        "fee": "0",
                        "deal_order_id": 2337653
                    }
                ]
            },
            "id": 1521169460
        }
        """
        if not order_id:
            order_id = 1
        sign = self.get_sign_two(api_key=settings.API_KEY,order_id=order_id)
        params = "api_key={}&sign={}&order_id={}".format(settings.API_KEY, sign, order_id)
        response = requests.post(ORDER_FINISHED_DETAIL, data=params)
        return response.json()
        
    def order_depth(self, market=settings.MARKET, limit=100, interval='1e-8'):
        response = requests.get("https://api.hotbit.io/api/v1/order.depth?market={}&limit={}&interval={}".format(market, limit, interval))
        return response.json()
    
    @authentication_required
    def pending_orders(self,  market=None, offset=settings.OFFSET, limit=settings.LIMIT):
        """
                {
            "error":null,
            "result":{
                "ETHBTC":{
                    "limit":50,
                    "offset":0,
                    "total":1,
                    "records":[
                        {
                            "id":8688803,    #order-ID
                            "market":"ETHBTC",
                            "source":"web",    #source identification of data request
                            "type":1,	       #type of order placement 1-limit order
                            "side":2,	       #sign of buyer and seller 1-seller，2-buyer
                            "user":15731,
                            "ctime":1526971722.164765, #Time of order establishment
                            "mtime":1526971722.164765, #Time of order establishment
                            "price":"0.080003",
                            "amount":"0.4",
                            "taker_fee":"0.0025",
                            "maker_fee":"0",
                            "left":"0.4",
                            "deal_stock":"0",
                            "deal_money":"0",
                            "deal_fee":"0",
                    "status":0    , #Sign of order status when 0x8 is true, it means the current order is cancelled, when 0x80 is true, it means that the current order is deducted by deductable tokens		    "fee_stock":"HTB",	#name of deductable token
                    "alt_fee":"0.5",	#Discount of the deductable token
                        "deal_fee_alt":"0.123" #amount deducted
                        }
                    ]
                }
            },
            "id":1526971756
        }

        """
        if market == None:
            market = settings.MARKET
        sign = self.get_sign(api_key=settings.API_KEY, market=market, offset=offset, limit=limit, secret_key=settings.SECRET_KEY)
        params = "api_key={}&sign={}&market={}&offset={}&limit={}".format(settings.API_KEY, sign, market, offset, limit)
        response = requests.post(ORDER_PENDING, data=params, headers=HEADERS)
        return response.json()
    
    @authentication_required   
    def order_finished(self, market=settings.MARKET, start_time=0, end_time=int(round(get_epoch_now(), 0)), offset=0, limit=1000, side=1):
        """
        Response:
        {
            "error": null,
            "result": {
                "id": 1,
                "ctime": 1535545564.4409361,#(秒)
                "ftime": 1535545564.525017,#(秒)
                "user": 15731,
                "market": "YCCETH",
                "source": "test",
                "type": 1,
                "side": 2,      # 1 = "sell"，2="buy"
                "price": "0.0000509",
                "amount": "1",
                "taker_fee": "0.001",
                "maker_fee": "0.001",
                "deal_stock": "1",
                "deal_money": "0.0000509",
                "deal_fee": "0.001",
            "status":0    , #Sign of order status when 0x8 is true, it means the current order is cancelled, when 0x80 is true, it means that the current order is deducted by deductable tokens   	"fee_stock":"HTB",	#Name of deductable token
            "alt_fee":"0.5",	#The discount of deductable token
            "deal_fee_alt":"0.123" #Amount deducted
            },
            "id": 1536050997
        }
        """
        if not market:
            market = self.market
        sign = self.get_sign_two(api_key=settings.API_KEY, market=market, start_time=start_time, end_time=end_time, offset=offset, limit=limit, side=side)
        params = "api_key={}&sign={}&market={}&start_time={}&end_time={}&offset={}&limit={}&side={}".format(settings.API_KEY, sign, settings.MARKET, start_time, end_time, offset, limit, side)
        response = requests.post(ORDER_FINISHED_LIST, data=params).json()
        return response
    
    

    def get_crypto_price(self, market=None):    
        CRYPTO_CURRENT_VALUE = float(requests.get("https://api.hotbit.io/api/v1/market.last?market=CTS/USDT").json().get('result'))
        return CRYPTO_CURRENT_VALUE
    
    def get_sign(self, *args, **kwargs):
        
        arguments_list = sorted(kwargs)
        sign_unhashed=""
        for arg in arguments_list:
            sign_unhashed += f"{arg}={kwargs[arg]}&"  
        sign_unhashed = sign_unhashed[:-1]
        
        hashlib.md5().digest()
        SIGN = hashlib.md5()
        RAW = sign_unhashed
        SIGN.update(RAW.encode('utf-8'))
        SIGN.digest()
        #########################################
        
        SIGN = str(SIGN.hexdigest()).upper()
        return SIGN
    
    def get_sign_two(self, *args, **kwargs):
        
        arguments_list = sorted(kwargs)
        sign_unhashed=""
        for arg in arguments_list:
            sign_unhashed += f"{arg}={kwargs[arg]}&"  
        sign_unhashed += "secret_key="+ settings.SECRET_KEY
        
        hashlib.md5().digest()
        SIGN = hashlib.md5()
        RAW = sign_unhashed
        SIGN.update(RAW.encode('utf-8'))
        SIGN.digest()
        #########################################
        
        SIGN = str(SIGN.hexdigest()).upper()
        return SIGN
    
 
 
class AuthenticationError(Exception):
        pass

class MarketClosedError(Exception):
    pass

class MarketEmptyError(Exception):
    pass
    