import requests
import hashlib
from pathlib import Path
import os
import dotenv
import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", passwd="1234")

SERVER_TIME = "https://api.hotbit.io/api/v1/server.time"
BALANCE_QUERY = "https://api.hotbit.io/api/v1/balance.query"
BALANCE_HISTORY = "https://api.hotbit.io/api/v1/balance.history"
ASSETS_LIST = "https://api.hotbit.io/api/v1/asset.list"
MARKET_LIST = "https://api.hotbit.io/api/v1/market.list"
MARKET_LAST = "https://api.hotbit.io/api/v1/market.last"
USER_DEALS = "https://api.hotbit.io/api/v1/market.user_deals"
STATUS_TODAY = "https://api.hotbit.io/api/v1/market.status_today"
MARKET_24_HR = "https://api.hotbit.io/api/v1/market.status24h"
MARKET_SUMMERY = "https://api.hotbit.io/api/v1/market.summary"

INPUT_LOWER_RANGE = 1.15131
INPUT_UPPER_RANGE = 1.15129

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
    





response = requests.get("{}?market=CTS/USDT".format(MARKET_LAST), data=PARAMS)
print(response)

print(response.content)
print(response.text)
print(response.json())



CRYPTO_CURRENT_VALUE = float(requests.get("https://api.hotbit.io/api/v1/market.last?market=CTS/USDT", data=PARAMS).json().get('result'))

print(CRYPTO_CURRENT_VALUE)

if CRYPTO_CURRENT_VALUE < INPUT_LOWER_RANGE:
    DIFFERENCE = INPUT_LOWER_RANGE - CRYPTO_CURRENT_VALUE
    print("Oversold! Seller aare greater then buyer ! please add buyer proportion to difference !")
    print("buy! buy! buy!")
    print(DIFFERENCE)
    
if CRYPTO_CURRENT_VALUE > INPUT_UPPER_RANGE:
    DIFFERENCE = CRYPTO_CURRENT_VALUE - INPUT_UPPER_RANGE
    print("Overbought! Buyer are greater than seller ! please sell your coins proportion to difference !")
    print("sell! sell! sell!")
    print(DIFFERENCE)
    
    
# time ,open, close, high, low ,volume, deal, market  
response = requests.get("https://api.hotbit.io/api/v1/market.kline?market=CTS/USDT&start_time=1634887815&end_time=1634887841&interval=60")
print(response.content)

# all the data about CTS
response = requests.get("https://api.hotbit.io/api/v1/market.status?market=CTS/USDT&period=10")
print(response.content)


#A account status of user
response = requests.post("https://api.hotbit.io/api/v1/balance.query", data=PARAMS2)
print(response.content)