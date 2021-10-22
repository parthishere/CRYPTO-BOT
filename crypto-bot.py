import requests
import hashlib
from pathlib import Path
import os
import dotenv

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

PARAMS = "api_key={}&sign={}&assets={}".format(API_KEY, SIGN, ASSETS)


INPUT_LOWER_RANGE = 1.15131
INPUT_UPPER_RANGE = 1.15129




response = requests.get("{}&market=CTS/USDT".format(MARKET_LAST), data=PARAMS)
print(response)

print(response.content)
print(response.text)
print(response.json())



CRYPTO_CURRENT_VALUE = requests.get("https://api.hotbit.io/api/v1/market.last?market=CTS/USDT", data=PARAMS).json().get('result')

print(CRYPTO_CURRENT_VALUE)