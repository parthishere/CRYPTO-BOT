import os, hashlib
from os.path import join
import dotenv
from pathlib import Path
import logging, psycopg2

# For Debugging purpose
DEBUG = True

# logging.INFO, logging.WARNING, logging.DEBUG
LOG_LEVEL = logging.INFO

# If set to yes then bot will buy also when the amount of bid and sell will be same 
# so the spead will increase between bidders and sellers
BUY_AGGRESIVELY = False # not ready yet

DEFAULT_CHANGE = 10

#You can set type of trading 
# "VOLUME" type trading depends on volume in Orderbook
# "PRICE" type trading depends on price fluctuation 
TYPE = "PRICE" 

BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)
    
# set secret_key and api_key in .env file
SECRET_KEY = os.environ['secret_key']
API_KEY = os.environ['api_key']
ASSETS = os.environ['assets'] or ["CTS/USDT"]

# Default value
# How much lower crypto price may go
INPUT_LOWER_RANGE = 2.0000
# How much higher price may go
INPUT_UPPER_RANGE = 2.100

# "BTC", "ETH" etc.
ASSET = "CTS"
# "BTC/USDT", "ETH/USDT" etc 
MARKET = "CTS/USDT"


# Maintain gap between Buyers Volume and Sellers Volume
MAINTAIN_SPREAD = True
# Max Spread
MIN_SPREAD = 0.01
# Min Spread
MAX_SPREAD = 0.5
# In Percent means at what threshold of difference between buyers and sellers should we start buying or selling
FLUCTUATION = 5  # 5%

# last open value of crypto before LAST_VALUE_PERIOD seconds
LAST_VALUE_PERIOD = 1296000 # 15 days


# How much order size you want to put in orderbook ?
# The orders will be in placed in pairs of MAX_ORDER_PAIRS
MAX_ORDER_PAIRS = 6

# Max limit of pending orders
MAX_PENDING_ORDERS = 100

CHECK_POSITION_LIMITS = True
MAX_POSITION = 20000
MIN_POSITION = 0

# How much price after decimal point.
PRICE_PRECISION = 8

# How much price Ratio will be bearable or amendable for relisting the existing order
RELIST_INTERVAL = 2


DEFAULT_BUSINESS= "deposit"

# Related to Hotbit API, If you dont know what it is then don't change values of variable
# Offset of Zero gives you all the data till last order or object
OFFSET = 0
LIMIT = 100
INTERVAL = 1
ISFEE = 0

# How much time the bot will sleep after one loop of execution
LOOP_INTERVAL = 1

#Don't change unless and until you know which file is which
WATCHED_FILES = [join('market_maker', 'exchange_interface.py'), join('market_maker', 'hotbit.py'), join('market_maker', 'ordermanager.py'), join('market_maker' ,'settings.py'), 'main.py']


def get_input_range():
    global INPUT_LOWER_RANGE, INPUT_UPPER_RANGE
    try:
        conn = psycopg2.connect(database=os.environ['DATABASE_NAME'], user=os.environ['DATABASE_USER'], password=os.environ['DATABASE_PASSWORD'], host=os.environ["DATABASE_HOST"], port="5432")

        cur = conn.cursor()
        cur.execute("SELECT id, min_lower_bound, max_upper_bound FROM app_cryptomodel ORDER BY id")
        print("The number of parts: ", cur.rowcount)
        row = cur.fetchall().pop()
        print(row)
        if cur.rowcount == row[0]:
            INPUT_LOWER_RANGE = round(row[1], 4)
            INPUT_UPPER_RANGE = round(row[2], 4)
            print(INPUT_LOWER_RANGE, INPUT_UPPER_RANGE)
            
    except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    finally:
        if conn is not None:
            conn.close()
