import requests, hashlib, datetime, time, dotenv, os, mysql.connector
from pathlib import Path
from pprint import pprint
import settings

try:
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="1234")
except:
    pass

SERVER_TIME = "https://api.hotbit.io/api/v1/server.time"
BALANCE_QUERY = "https://api.hotbit.io/api/v1/balance.query"
BALANCE_HISTORY = "https://api.hotbit.io/api/v1/balance.history"
ASSETS_LIST = "https://api.hotbit.io/api/v1/asset.list"

ORDER_PUT_LIMIT = "https://api.hotbit.io/api/v1/order.put_limit" # Limit Order Transaction
ORDER_CANCEL = "https://api.hotbit.io/api/v1/order.cancel" # Cancel Transaction
ORDER_BULK_CANCEL = "https://api.hotbit.io/api/v1/order.batch_cancel" # Cancel transactions in large quantities
ORDER_DEALS = "https://api.hotbit.io/api/v1/order.deals" # Obtain the details of settled orders
ORDER_FINISHED_DETAIL = "https://api.hotbit.io/api/v1/order.finished_detail" # Check finished orders according to order number
ORDER_BOOK = "https://api.hotbit.io/api/v1/order.book" # Have to add parameters see doc! # obtain list of transaction
ORDER_PENDING = "https://api.hotbit.io/api/v1/order.pending" # CHECK UNEXECUTED ORDERS

MARKET_LIST = "https://api.hotbit.io/api/v1/market.list" # Obtain the list of transaction pairs
MARKET_LAST = "https://api.hotbit.io/api/v1/market.last" # have to add paramer # obtain the latest price of designated transaction pair
USER_DEALS = "https://api.hotbit.io/api/v1/market.user_deals" # check the user's transaction records
MARKET_KLINE = "https://api.hotbit.io/api/v1/market.kline" # Parameters required # Check K Chart
MARKET_STATUS = "https://api.hotbit.io/api/v1/market.status" # obtain the latest status of the market during the designated period of time in the past,l such as latest range of increase and decline, trading volume, highest/lowest price etc. # para required
MARKET_24_HR = "https://api.hotbit.io/api/v1/market.status24h" # obtain today's market status 
MARKET_SUMMERY = "https://api.hotbit.io/api/v1/market.summary" # market summary

ALLTICKER = "https://api.hotbit.io/api/v1/allticker" # obtain the latest trading informnation of all transaction pairs in the market


PARAMS, PARAMS2 = None, None

def get_params():
    global PARAMS, PARAMS2
    BASE_DIR = Path(__file__).resolve().parent
    print(BASE_DIR)
    dotenv_file = os.path.join(BASE_DIR, ".env")
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)

    hashlib.md5().digest()
    SIGN = hashlib.md5()

    SECRET_KEY = os.environ['secret_key']
    API_KEY = os.environ['api_key']
    ASSETS = os.environ['assets']

    RAW = str("api_key={}&assets={}&secret_key={}".format(API_KEY, ASSETS, SECRET_KEY))
    SIGN.update(RAW.encode('utf-8'))
    SIGN.digest()

    SIGN = str(SIGN.hexdigest()).upper()

    PARAMS2 = f"api_key={API_KEY}&assets={ASSETS}&sign={SIGN}"
    PARAMS = "api_key={}&sign={}&assets={}".format(API_KEY, SIGN, ASSETS)

if (PARAMS or PARAMS2) is None or (PARAMS or PARAMS2 == ""):
    print('getting params')
    get_params()



def get_input_range(lower_range=settings.INPUT_UPPER_RANGE, upper_range=settings.INPUT_UPPER_RANGE):
    global INPUT_LOWER_RANGE, INPUT_UPPER_RANGE
    INPUT_UPPER_RANGE = upper_range
    INPUT_LOWER_RANGE = lower_range
    CRYPTO_CURRENT_VALUE = float(requests.get("https://api.hotbit.io/api/v1/market.last?market=CTS/USDT", data=PARAMS).json().get('result'))
    if CRYPTO_CURRENT_VALUE < INPUT_LOWER_RANGE or CRYPTO_CURRENT_VALUE > INPUT_UPPER_RANGE:
        raise Exception("Range should be bounded to crypto current value")


def get_server_time():
    return requests.get(SERVER_TIME).json()


def get_epoch_time(year, month, day, hours, minutes, seconds):
    epoch_time = datetime.datetime(year, month, day, hours, seconds).timestamp()
    return epoch_time


def get_epoch_now():
    epoch_time = datetime.datetime(time.localtime().tm_year, time.localtime().tm_mon, time.localtime().tm_mday, time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec).timestamp()
    return epoch_time


class Account():
    
    def __init__(self):
        pass

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
        parameter = "api_key={}&sign={}&assets={}".format(settings.API_KEY, settings.SIGN, settings.ASSETS)
        response = requests.post(BALANCE_QUERY, data=parameter)
        return response.json()



class Order():
    
    def __init__(self):
        pass
    
    def check_market_open(self):
        resopose = requests.get()
    
    def sell(self, amount=0, price=0):
        side = 1 # 1 for sell and 2 for buy
        params = "api_key={}&sign={}&market={}&side={}&amount={}&price={}&isfee={}".format(settings.API_KEY, settings.SIGN, side, amount, price, settings.ISFEE)
        response = requests.post(ORDER_PUT_LIMIT, data=params)
    
    def buy(self, amount=0, price=0):
        side = 2 # 1 for sell and 2 for buy
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
           
        
        
class Market():
    
    def __init__(self):
        pass

    def market_status_today(self):
        response = requests.get("https://api.hotbit.io/api/v1/market.status_today?market={CTS/USDT}")
        return response.json()
   
 
    def market_summery(self):
        crypto = "CTS/USDT"
        response = requests.get("https://api.hotbit.io/api/v1/market.summary?markets={CTS/USDT}")
        return response.json()
  
    
    def market_status_24h(self):
        crypto="CTS/USDT"
        response = requests.get("https://api.hotbit.io/api/v1/market.status_today?market=CTS/USDT")
        return response.json()


    def market_kline(self, start_time, end_time, interval):
        crypto = "CTS/USDT"
        start_time = 0
        end_time = 0
        response = requests.get("https://api.hotbit.io/api/v1/market.kline?market=ETH/BTC&start_time=1521100000&end_time=1521101193&interval=60") 
        return response.json()
    
    def market_last_value(self, market=settings.MARKET):
        params = None
        reponse = requests.get("https://api.hotbit.io/api/v1/market.last?market=CTS/USDT", data=PARAMS)
        return reponse.json()


response = requests.get("{}?market=CTS/USDT".format(MARKET_LAST), data=PARAMS)
print(response)

print(response.content)
print(response.text)
print(response.json())



CRYPTO_CURRENT_VALUE = float(requests.get("https://api.hotbit.io/api/v1/market.last?market=CTS/USDT", data=PARAMS).json().get('result'))

print(CRYPTO_CURRENT_VALUE)

if CRYPTO_CURRENT_VALUE < settings.INPUT_LOWER_RANGE:
    DECREASE = INPUT_LOWER_RANGE - CRYPTO_CURRENT_VALUE
    INCREASE = 0
    print("Oversold! Seller aare greater then buyer ! please add buyer proportion to difference !")
    print("buy! buy! buy!")
    # Selling logic ( like after we bought a batch our bot will continue to buy the coins cause still the price is higher for few seconds will be a huge problem )
    print(DECREASE)
    
elif CRYPTO_CURRENT_VALUE > settings.INPUT_UPPER_RANGE:
    INCREASE = CRYPTO_CURRENT_VALUE - INPUT_UPPER_RANGE
    DECREASE = 0
    print("Overbought! Buyer are greater than seller ! please sell your coins proportion to difference !")
    print("sell! sell! sell!")
    # Selling logic ( like after we sold a batch our bot will continue to sell the coins cause still the price is lower for few seconds will be a huge problem )
    print(INCREASE)
    
    
# # time ,open, close, high, low ,volume, deal, market  
# response = requests.get("https://api.hotbit.io/api/v1/market.kline?market=CTS/USDT&start_time=1634887815&end_time=1634887841&interval=60")
# print(response.content)

# # all the data about CTS
# response = requests.get("https://api.hotbit.io/api/v1/market.status?market=CTS/USDT&period=10")
# print(response.content)


# #A account status of user
# response = requests.post("https://api.hotbit.io/api/v1/balance.query", data=PARAMS2)
# print(response.content)

market = Market()
account = Account()
order = Order()