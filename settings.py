import os

SECRET_KEY = os.environ['secret_key']
API_KEY = os.environ['api_key']
ASSETS = os.environ['assets']


CRYPTO_MARKET = ["CTS/USDT"]
CRYPTO_NAME = "CTS"

INPUT_LOWER_RANGE = 1.15131
INPUT_UPPER_RANGE = 1.151

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


TIMEZONE = 'IST'
OFFSET = ""
LIMIT = None
INTERVAL = 1