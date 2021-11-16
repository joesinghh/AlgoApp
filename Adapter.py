from kite_api import Kite
from ifl_api import MarketApi
import requests
import json
import logging.config

logging.config.fileConfig('.\\Logs\\log.ini',disable_existing_loggers=False)
logging.getLogger(__name__)

class AdapterApi():

    def __init__(self, cls):
        self.cls = cls
        self.enctoken = None
        if isinstance(self.cls,MarketApi):
            self.value = 1
        elif isinstance(self.cls,Kite):
            self.value = 2
        else:
            self.value = None

    def place_order(self,**kwargs):
        self.__dict__.update(kwargs)

        if self.value==1:
            
            self.cls.place_order(self.id_,self.slide,self.q)

        elif self.value==None:
            self.get_enctoken()
            data = f"tradingsymbol={self.tradingsymbol}&transaction_type={self.slide}&order_type=MARKET&quantity={self.size*self.q}&disclosed_quantity=1&exchange=NFO&product={self.product_type}"
            header = {
                'Content-Type':'application/x-www-form-urlencoded',
                'Authorization':f'enctoken {self.enctoken}'
            }
 
        
            r = requests.post('https://kite.zerodha.com/oms/orders/regular',data=data,headers=header,verify=False)

            
            if r.status_code>300:
                print(r.json())
                raise Exception(r.json()['message'])
                

        elif self.value==2:
            self.cls.place_order(exchange=self.exchange,symbol=self.symbol,t_type=self.ttype,quantity=self.q)
    
    def get_enctoken(self):
        with open(".\\Tokens\\enctoken.txt","r") as f:
            token = f.read()
            if not token:
                self.login_kitefree()
            else:
                self.enctoken = token


    def login_kitefree(self):
        f = open(".\\Config\\kitefree.json")
        data = json.load(f)

        userid = data['userid']
        password = data['password']
        twofa = data['twofa']

        session = requests.Session()
        
        login1 = session.post('https://kite.zerodha.com/api/login',data={"user_id":userid,"password":password})
        if login1.status_code>=300:
            raise Exception(login1.json()['message'])
            
        request_id = login1.json()['data']['request_id']
        
        twofa_data = {
            "request_id":request_id,
            "user_id":userid,
            "twofa_value":twofa
        }
        login2 = session.post("https://kite.zerodha.com/api/twofa",data=twofa_data)
        if login2.status_code>=300:
            raise Exception(login2.json()['message'])
        
        
        enctoken = session.cookies['enctoken']

        with open(".\\Tokens\\enctoken.txt","w")as file:
            file.write(enctoken)
            self.enctoken = enctoken
            print("Login Successful, enctoken generated")
            
if __name__=="__main__":
    a = AdapterApi(None)

    a.login_kitefree()
