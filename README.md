# btcmarkets-client
A python wrapper to the btcmarkets.com API

# Sample Usage
```python
from btcmarket import *

pk = "<your public key>"
sk = "<your private/secret key>"

# Initialise a BTCMarket with your public key and secret key
market = BTCMarket(pk, sk)

# Get a price of BTC in AUD
print(market.get_price("BTC", "AUD"))

# Get the order book for BTC in AUD
print(market.get_order_book("BTC", "AUD"))

# Buy 0.001 BTC @ 230 AUD
print(market.buy("BTC", "AUD", 230, 0.001, "Limit", "1"))

# Sell 0.001 BTC @ 240 AUD
print(market.sell("BTC", "AUD", 240, 0.001, "Limit", "1"))

# Cancel orders with IDs 1, 2, 3 and 4
print(market.cancel_orders([1, 2, 3, 4]))

# Get account balances
balances = market.get_account_balances()
for balance in balances:
    print(balance)

# Get your trading fee
print(market.get_trading_fee())

# Get trades since trade with id 995479884
trades = market.get_trades("BTC", "AUD", since=995479884)
for trade in trades:
    print(trade)

# Get orders
myorders = market.get_orders("BTC", "AUD", 20, 0)
for order in myorders:
    print(order)

# Get open orders
myorders = market.get_open_orders("XRP", "AUD", 10, 0)
for order in myorders:
    print(order)

```
