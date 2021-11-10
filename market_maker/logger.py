import logging
from market_maker import settings

logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

