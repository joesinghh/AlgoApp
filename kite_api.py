from kiteconnect import KiteConnect
from dotenv import load_dotenv
import os
import re
import requests
import pandas as pd
import json
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class Kite():
    instruments = None
    def __init__(self):
        f = open('.\\Config\\kite.json')
        data = json.load(f)
        self.key = data["kitekey"]
        self.secretkey = data["secretkey"] 
        self.cls = KiteConnect(api_key=self.key)
        
        self.r_key = None
        self.session = None
        self.set_token()
        
    def set_token(self):
        with open("kite_access.txt","r") as f:
            self.r_key = f.read()

        with open("kite_session.txt","r") as f:
            self.session = f.read()
        self.cls.set_access_token(self.session)

    def login(self):
        with open("kite.txt" ,"w") as f:
            self.r_key  = int(re.findall(r"[0-9]+",self.cls.login_url())[0])
            f.write(self.r_key)
            
        with open("kite_session.txt","w") as f:
            self.session = self.cls.generate_session(self.r_key,self.secretkey)['access_token']
            f.write(self.session)


    def get_id(self,symbol):
        return Kite.instruments['instrument_token'][Kite.instruments.tradingsymbol == symbol]

    def get_symbol(self,instru_id):
        return Kite.instruments['tradingsymbol'][Kite.instruments.instrument_token == instru_id]

    def get_lot(self,symbol):
        return Kite.instruments['lot_size'][Kite.instruments.tradingsymbol == symbol]

    def get_expiry(self,symbol):
        return Kite.instruments['expiry'][Kite.instruments.tradingsymbol == symbol]
        

    def get_quote(self,symbol,exchange):
        ins = symbol+":"+exchange
        r = self.cls.quote(ins)
        bids = [r["data"][ins]["depth"]["buy"][0]["price"],r["data"][ins]["depth"]["buy"][1]["price"],r["data"][ins]["depth"]["buy"][2]["price"]]
        sells = [r["data"][ins]["depth"]["sell"][0]["price"],r["data"][ins]["depth"]["sell"][1]["price"],r["data"][ins]["depth"]["sell"][2]["price"]]
        return bids, sells
  
    def place_order(self, variety='regular', exchange='NFO', symbol='FSL', t_type='BUY', quantity=1, product="MIS", order_type="MARKET"):
        self.cls.place_order(variety, exchange, symbol, t_type, quantity, product, order_type)
    

    def set_instruments(self):
        Kite.instruments=pd.DataFrame(self.cls.instruments("NSE"))
