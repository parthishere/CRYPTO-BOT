import os, hashlib
import dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)
    

SECRET_KEY = os.environ['secret_key']
API_KEY = os.environ['api_key']
ASSETS = os.environ['assets']

#########################################
hashlib.md5().digest()
SIGN = hashlib.md5()
RAW = str("api_key={}&assets={}&secret_key={}".format(API_KEY, ASSETS, SECRET_KEY))
SIGN.update(RAW.encode('utf-8'))
SIGN.digest()
#########################################

SIGN = str(SIGN.hexdigest()).upper()

INPUT_LOWER_RANGE = 1.15131
INPUT_UPPER_RANGE = 1.151

ASSETS = ["CTS/USDT"]
ASSET = "CTS"
MARKET = "CTS/USDT"

TIMEZONE = 'IST'
DEFAULT_BUSINESS= "deposit"
OFFSET = 0
LIMIT = 0
INTERVAL = 1
ISFEE = 0


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
