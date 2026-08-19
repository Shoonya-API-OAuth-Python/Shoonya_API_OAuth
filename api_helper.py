from NorenRestApiPy.NorenApi import NorenApi
from threading import Timer
import pandas as pd
import time
import concurrent.futures
import requests
from functools import partial
api = None

class Order:
     def __init__(self, buy_or_sell:str = None, product_type:str = None,
                 exchange: str = None, tradingsymbol:str =None, 
                 price_type: str = None, quantity: int = None, 
                 price: float = None,trigger_price:float = None, discloseqty: int = 0,
                 retention:str = 'DAY', remarks: str = "tag",
                 order_id:str = None):
        self.buy_or_sell=buy_or_sell
        self.product_type=product_type
        self.exchange=exchange
        self.tradingsymbol=tradingsymbol
        self.quantity=quantity
        self.discloseqty=discloseqty
        self.price_type=price_type
        self.price=price
        self.trigger_price=trigger_price
        self.retention=retention
        self.remarks=remarks
        self.order_id=None
    #print(ret)
    
def get_time(time_string):
    data = time.strptime(time_string,'%d-%m-%Y %H:%M:%S')
    return time.mktime(data)

class NorenApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientAPI/', websocket='wss://api.shoonya.com/NorenWSAPI/')
        global api
        api = self

        # Order latecy 
        _session = requests.Session()
        _session.headers.update({"Connection": "keep-alive"})
        _adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=0)
        _session.mount("https://", _adapter)
        _session.mount("http://", _adapter)

        requests.get = partial(_session.get,timeout=(3,5))
        requests.post = partial(_session.post,timeout=(3,5))
        #  end pooled session setup 

    def place_basket(self, orders):
        resp_err = 0
        resp_ok  = 0
        result   = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.place_order, order): order for order in  orders}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
            try:
                result.append(future.result())
            except Exception as exc:
                print(exc)
                resp_err = resp_err + 1
            else:
                resp_ok = resp_ok + 1
        return result
                
    def placeOrder(self,order: Order):
        ret = NorenApi.place_order(self, buy_or_sell=order.buy_or_sell, product_type=order.product_type,
                            exchange=order.exchange, tradingsymbol=order.tradingsymbol, 
                            quantity=order.quantity, discloseqty=order.discloseqty, price_type=order.price_type, 
                            price=order.price, trigger_price=order.trigger_price,
                            retention=order.retention, remarks=order.remarks)
        #print(ret)
        return ret
