from kite_api import Kite
from ifl_api import MarketApi
import requests

class AdapterApi():
    def __init__(self, cls):
        self.cls = cls
        if isinstance(self.cls,MarketApi):
            self.value = 1
        elif isinstance(self.cls,Kite):
            self.value = 2
        else:
            self.value = None

        # print("CLASS IS ",self.cls)
        

    def place_order(self,**kwargs):
        self.__dict__.update(kwargs)
        print(kwargs)

        if self.value==1:
            self.cls.place_order(self.id_,self.slide,self.q)

        elif self.value==None:
            data = f"tradingsymbol={self.tradingsymbol}&transaction_type={self.slide}&order_type=MARKET&quantity={self.size*self.q}&disclosed_quantity=1&exchange=NFO&product=MIS"
            header = {
                'Content-Type':'application/x-www-form-urlencoded',
                'Authorization':f'enctoken {self.enctoken}'
            }
            # print(self.tradingsymbol)
        
            r = requests.post('https://kite.zerodha.com/oms/orders/regular',data=data,headers=header,verify=False)
            print(r.status_code)
            # print(r.json())
            if r.status_code>300:
                raise Exception("Can not place order")
            else:
                print(r.json()) 

        elif self.value==2:
            self.cls.place_order(exchange=self.exchange,symbol=self.symbol,t_type=self.ttype,quantity=self.q)


if __name__=="__main__":
    a = AdapterApi(None)

    enctoken = '3f8HTtmNKzdu1RH0O+KQFCNELlOC1wKD/e4X5VXyuD5GUOVnhvj8taL1M1Q2J1hbw07ICz2FYdJbtLoZuL3cpRh2q+vArbykdgpcXE9aAU0E6/xg7K9FEg=='
    q = 1
    tradingsymbol = 'BANKNIFTY21AUG35500CE'
    slide = 'BUY'
    a.place_order(q=q,tradingsymbol=tradingsymbol,enctoken=enctoken,slide=slide)




        
    
    

