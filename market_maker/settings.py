import os, hashlib
from os.path import join
import dotenv
from pathlib import Path
import logging


DEBUG = True

LOG_LEVEL = logging.INFO

BUY_AGGRESIVELY = False


BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)
    

SECRET_KEY = os.environ['secret_key']
API_KEY = os.environ['api_key']
ASSETS = os.environ['assets'] or ["CTS/USDT"]


INPUT_LOWER_RANGE = 1.15131
INPUT_UPPER_RANGE = 1.151


ASSET = "CTS"
MARKET = "CTS/USDT"


# Maintain gap between Buyers Volume and Sellers Volume
MAINTAIN_SPREAD = True
# Max Spread
MIN_SPREAD = 0.01
# Min Spread
MAX_SPREAD = 0.5
# In Percent means at what threshold should we start buying or selling
FLUCTUATION = 5  

# last open value of crypto before LAST_VALUE_PERIOD seconds
LAST_VALUE_PERIOD = 5 


# How much order size you want to put in orderbook ?
MAX_ORDER_PAIRS = 6
MIN_ORDER_SIZE = 0
MAX_ORDER_SIZE = -1 # -1 = no Limit



CHECK_POSITION_LIMITS = True
MAX_POSITION = 0
MIN_POSITION = 0

# How much price after decimal point.
PRICE_PRECISION = 8

RELIST_INTERVAL = 2


TIMEZONE = 'IST'
DEFAULT_BUSINESS= "deposit"
OFFSET = 0
LIMIT = 100
INTERVAL = 1
ISFEE = 1

LOOP_INTERVAL = 1

WATCHED_FILES = [join('market_maker', 'exchange_interface.py'), join('market_maker', 'hotbit.py'), join('market_maker', 'ordermanager.py'), join('market_maker' ,'settings.py')]
