import requests
from market_maker import hotbit, settings

# side = 2 matlab buy

params = "api_key={}&sign={}&market={}&side=1&amount=0.01&price=1.5&isfee={}".format(settings.API_KEY, settings.SIGN, settings.MARKET, settings.ISFEE)
param2 = "api_key=34e2bb5d-2047-8ab1-67395b7934a798c3&sign=84eb6f6b2e85d76c9864cba62adb806b&market=CTS/USDT&side=1&amount=0.01&price=1.5&isfee=0"

response = requests.post(hotbit.ORDER_PUT_LIMIT, data=param2, headers=hotbit.HEADERS)

# response2 = requests.post(hotbit.ORDER_PUT_LIMIT, data="api_key=34e2bb5d-2047-8ab1-67395b7934a798c3&sign=84eb6f6b2e85d76c9864cba62adb806b&market=CTS/USDT&side=2&amount=0.01&price=1.5&isfee=0", headers=hotbit.HEADERS)

# response3 = requests.post("https://api.hotbit.io/api/v1/order.put_limit", data="api_key=34e2bb5d-2047-8ab1-67395b7934a798c3&sign=84eb6f6b2e85d76c9864cba62adb806b&market=CTS/USDT&side=2&amount=0.01&price=1.5&isfee=0")

print(response.json())
# print(response2.json())
# print(response3.json())


# import websocket
# import json
# from websocket import create_connection

# websocket.enableTrace(True)
# ws = create_connection('wss://ws.hotbit.io')

# result = ws.recv()
# print('Result: {}'.format(result))

# ws.send(json.dumps({
#     "method":"server.ping",
#     "params":[],
#     "id":100
# }))
# result = ws.recv()
# print('Result: {}'.format(result))