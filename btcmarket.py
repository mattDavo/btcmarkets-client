import requests
import base64
import time
import hashlib
import hmac
import json
from typing import List
from datetime import datetime

number_converter = 100000000

class Price(object):
    def __init__(self, best_bid, best_ask, last_price, currency, instrument, timestamp, vol24h):
        self._best_bid = best_bid
        self._best_ask = best_ask
        self._last_price = last_price
        self._currency = currency
        self._instrument = instrument
        self._timestamp = timestamp
        self._vol24hr = vol24h
    
    def __str__(self):
        price_str = self._instrument + "\n"
        price_str += "Last Price: " + str(self._last_price) + " " + self._currency + "\n"
        price_str += "Best Bid: " + str(self._best_bid) + " " + self._currency + "\n"
        price_str += "Best Ask: " + str(self._best_ask) + " " + self._currency + "\n"
        # price_str += "Exchange: " + self._instrument + "/" + self._currency + "\n"
        price_str += "24 Hour Volume: " + str(self._vol24hr) +  " " + self._instrument
        return price_str


class Order(object):
    def __init__(self, instrument, currency, price, vol, order_side):
        self._instrument = instrument
        self._currency = currency
        self._price = price
        self._vol = vol
        self._order_side = order_side
    
    def __str__(self):
        order_str = self._order_side + " for " + str(self._vol) + " " + self._instrument + " @ " + \
            str(self._price) + " " + self._currency + "\n"
        return order_str


class MyOrder(Order):
    def __init__(self, instrument, currency, price, vol, order_side, id):
        Order.__init__(self, instrument, currency, price, vol, order_side)
        self._id = id


class Balance(object):
    def __init__(self, currency, balance, pending_funds):
        self._currency = currency
        self._balance = balance
        self._pending_funds = pending_funds
    
    def __str__(self):
        balance_str = "Balance: " + str(self._balance) + " " + self._currency + "    Pending Funds: " + \
            str(self._pending_funds) + " " + self._currency + "\n"
        return balance_str


class Account(object):
    def __init__(self, accounts):
        self._accounts = accounts
    
    def __str__(self):
        account_str = "Account Balances:\n"
        for account in self._accounts:
            account_str += str(account)
        return account_str


class OrderBook(object):
    def __init__(self, instrument, currency, bids, asks):
        self._instrument = instrument
        self._currency = currency
        self._bids = bids
        self._asks = asks
    
    def __str__(self):
        order_book_str = "Order book for " + self._instrument + "/" + self._currency + " exchange\n"
        order_book_str += "Bids\n"
        for bid in self._bids:
            order_book_str += str(bid)
        order_book_str += "Asks\n"
        for ask in self._asks:
            order_book_str += str(ask)
        return order_book_str


class Trade(object):
    def __init__(self, tid, instrument, currency, amount, price, date):
        self._tid = tid
        self._instrument = instrument
        self._currency = currency
        self._amount = amount
        self._price = price
        self._date = datetime.fromtimestamp(date)
    
    def __str__(self):
        trade_str = "ID: " + str(self._tid) + "  " + str(self._amount) + " " + self._instrument + \
        " bought @ " + str(self._price) + " " + self._currency + " at " + str(self._date)
        return trade_str


class BTCMarketAPI(object):
    def __init__(self, pk, sk):
        self._server = "https://api.btcmarkets.net"
        self._timeout = 20000
        self._pk = pk
        self._sk = sk
    
    def auth_sign(self, uri, data=None):
        """Returns the headers for a HTTP request that requires authentication"""
        timestamp = str(int(time.time() * 1000))
        request_to_sign = ""
        if data == None:
            request_to_sign = uri + "\n" + timestamp + "\n"
        else:
            request_to_sign = uri + "\n" + timestamp + "\n" + json.dumps(data).replace(" ", "")
        
        signature = base64.b64encode(hmac.new(base64.b64decode(self._sk), request_to_sign.encode('utf-8'),
            digestmod=hashlib.sha512).digest())
        
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': 'btc markets python client',
            'accept-charset': 'utf-8',
            'apikey': self._pk,
            'signature': signature,
            'timestamp': timestamp
        }
        return headers
    
    def post_request(self, uri, data):
        """Creates a POST request"""
        headers = self.auth_sign(uri, data=data)
        
        r = requests.post(self._server + uri, headers=headers, json=data)
        request_json = r.json()
        if request_json["success"] != True:
            print(request_json)
            return None
        
        return request_json
    
    def get_request(self, uri):
        """Creates a GET request and returns the json dict"""
        r = requests.get(self._server + uri)
        return r.json()
    
    def get_request_auth(self, uri):
        """Creates a GET request that requires authentication and returns the json dict"""
        headers = self.auth_sign(uri)
        r = requests.get(self._server + uri, headers=headers)
        return r.json()


class BTCMarket(BTCMarketAPI):
    def __init__(self, pk, sk):
        BTCMarketAPI.__init__(self, pk, sk)
    
    def get_price(self, instrument, currency):
        """Gets the price of instrument in currency"""
        price_json = self.get_request("/market/" + instrument + "/" + currency + "/tick")
        if price_json ==  None:
            return None
        return Price(price_json["bestBid"], price_json["bestAsk"], price_json["lastPrice"], 
            price_json["currency"], price_json["instrument"], price_json["timestamp"],
            price_json["volume24h"])
    
    def buy(self, instrument, currency, price, vol, order_type, client_request_id) -> MyOrder:
        """Creates a buy order for the instrument paid in currency @ price of volumem vol."""
        if vol < 0.001:
            raise(ValueError("Volume must be at least 0.001"))
        if order_type != "Limit" and order_type != "Market":
            raise(ValueError("Order Type must be either Limit or Market"))
        data = {
            "currency": currency,
            "instrument": instrument,
            "price": int(number_converter * price),
            "volume": int(number_converter * vol),
            "orderSide": "Bid",
            "ordertype": order_type,
            "clientRequestId": client_request_id
        }
        
        uri = "/order/create"
        
        buy_data = self.post_request(uri, data)
        
        if buy_data == None:
            return None
        
        return MyOrder(instrument, currency, price, vol, "Bid", buy_data["id"])
    
    def sell(self, instrument, currency, price, vol, order_type, client_request_id) -> MyOrder:
        """Creates a sell order for the instrument paid in currency @ price of volumem vol."""
        if vol < 0.001:
            raise(ValueError("Volume must be at least 0.001"))
        if order_type != "Limit" and order_type != "Market":
            raise(ValueError("Order Type must be either Limit or Market"))
        data = {
            "currency": currency,
            "instrument": instrument,
            "price": int(number_converter * price),
            "volume": int(number_converter * vol),
            "orderSide": "Ask",
            "ordertype": order_type,
            "clientRequestId": client_request_id
        }
        uri = "/order/create"
        
        sell_data = self.post_request(uri, data)
        
        if sell_data == None:
            return None
        
        return MyOrder(instrument, currency, price, vol, "Ask", buy_data["id"])
    
    def cancel_orders(self, order_ids: List[int]):
        """Cancels the orders with ids in order_ids"""
        if len(order_ids) == 0:
            raise(ValueError("There must be at least one order id"))
        data = {
            "orderIds": order_ids
        }
        uri = "/order/cancel"
        
        cancel_data = self.post_request(uri, data)
        
        if cancel_data == None:
            return [False for i in range(len(order_ids))]
        
        return [order["success"] for order in cancel_data["responses"]]
    
    def get_order_book(self, instrument, currency):
        """Returns an order book object for the instrument/currency exchange"""
        order_book = self.get_request("/market/" + instrument + "/" + currency + "/orderbook")
        bids = []
        asks = []
        for bid in order_book["bids"]:
            bids.append(Order(instrument, currency, bid[0], bid[1], "Bid"))
        for ask in order_book["asks"]:
            asks.append(Order(instrument, currency, ask[0], ask[1], "Ask"))
        return OrderBook(instrument, currency, bids, asks)
    
    def get_account_balances(self):
        """Returns a list of Balances"""
        account_data = self.get_request_auth("/account/balance")
        balances = []
        for account in account_data:
            balances.append(Balance(account["currency"], account["balance"] / number_converter,
                account["pendingFunds"] / number_converter))
        return balances
    
    def get_trading_fee(self) -> float:
        """Returns the trading fee"""
        trading_fee_data = self.get_request_auth("/account/AUD/AUD/tradingfee")
        return trading_fee_data["tradingFeeRate"]/number_converter
    
    def get_trades(self, instrument, currency, since=None):
        """Returns trades of instrument/currency optionally since a trade_id"""
        trades_data = None
        if since == None:
            trades_data = self.get_request("/market/" + instrument + "/" + currency + "/trades")
        else:
            trades_data = self.get_request("/market/" + instrument + "/" + currency + "/trades" + \
                "?since=" + str(since))
        
        trades = []
        for trade in trades_data:
            trades.append(Trade(trade["tid"], instrument, currency, trade["amount"],
                trade["price"], trade["date"]))
        return trades
        
        
