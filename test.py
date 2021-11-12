import requests
from market_maker import hotbit, settings


params = "api_key={}&sign={}&market={}&side=2&amount=0.01&price=1.5&isfee={}".format(settings.API_KEY, settings.SIGN, settings.MARKET, settings.ISFEE)
param2 = "api_key=34e2bb5d-2047-8ab1-67395b7934a798c3&sign=84eb6f6b2e85d76c9864cba62adb806b&market=CTS/USDT&side=2&amount=0.01&price=1.5&isfee=0"
response = requests.post(hotbit.ORDER_PUT_LIMIT, data=param2, headers=hotbit.HEADERS)
print(response.json())