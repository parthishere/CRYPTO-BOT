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


# Maintain gap between Buyers Volume and Sellers Volume
MAINTAIN_SPREAD = False
# Max Spread
MIN_SPREAD = 0.01
# Min Spread
MAX_SPREAD = 0.05

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
PRICE_PRECISION = 4


TIMEZONE = 'IST'
DEFAULT_BUSINESS= "deposit"
OFFSET = 0
LIMIT = 0
INTERVAL = 1
ISFEE = 0
