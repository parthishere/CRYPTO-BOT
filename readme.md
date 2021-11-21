Hotbit Market Maker
This is market making bot using Hotbit.

A Hotbit object wrapping the REST APIs.
All data is realtime and efficiently fetched via the REST. This is the fastest way to get market data.
Orders may be created, queried, and cancelled via Hotbit.buy(), Hotbit.sell(), Hotbit.cancel_order() and the like.
Withdrawals may be requested.
Connection errors and Hotbit reconnection is handled for you.
Permanent API Key support is included.
A scaffolding for building your own trading strategies.
Out of the box, a simple market making strategy is implemented that blankets the bid and ask volume.
More complicated strategies are up to the user. Try incorporating index data, query other markets to catch moves early.
Develop on Testnet first! Testnet trading is completely free and is identical to the live market.

Hotbit is not responsible for any losses incurred when using this code. Do not use this code for real trades unless you fully understand what it does and what its caveats are. It does not make smart decisions.

Getting Started
Create a Testnet Hotbit Account and deposit some TBTC.

Install: pip install -r requirements.txt. It is strongly recommeded to use a virtualenv.

Modify settings.py to tune parameters.

Edit settings.py to add your Hotbit API Key and Secret and change bot parameters.

Note that user/password authentication is not supported.
Run with DEBUG=True to test cost and spread.
Run it: python main.py

Satisfied with your bot's performance? Create a live API Key for your Hotbit account, set the BASE_URL and start trading!

Operation Overview
This market maker works on the following principles:

The market maker tracks the last bidVolume and askVolume of the quoted instrument to determine where to start quoting.
If the buying orders are greater than selling orders (here volume) price will likely to increace gradually.
so bot will place sell order to overcome the selling orders, and so is vice verse. The prices will be predicated on current price as well as lowest selling price in market.

Based on parameters set by the user, the bot creates a descriptions of orders it would like to place.
If settings.MAINTAIN_SPREADS is set, the bot will start inside the current spread and work outwards.
Otherwise, spread is determined by interval calculations.
If the user specifies position limits, these are checked. If the current position is beyond a limit, the bot stops quoting that side of the market.
These order descriptors are compared with what the bot has currently placed in the market.
If an existing order can be amended to the desired value, it is amended.
Otherwise, a new order is created.
Extra orders are canceled.
The bot then prints details of contracts traded, pending orders, delta and total delta.
Simplified Output
The following is some of what you can expect when running this bo