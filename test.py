import requests
import os
from dotenv import load_dotenv

load_dotenv()

null = 0
false = False
true = True
#market data login
# r = requests.post("https://ttblaze.iifl.com/apimarketdata/auth/login",json = keyinfo)

class MarketApi(object):

    def __init__(self):
        self.secretKey = str(os.getenv("secretKey"))
        self.appKey = str(os.getenv("appKey"))
        self.source = str(os.getenv("source"))
        self.instrument_id = None
        self.file  = "token.txt"
        self.baseurl = "https://ttblaze.iifl.com/apimarketdata"
        self.getquoteurl = "/instruments/quotes"
        self.loginpath = "/auth/login"
        self.token = None
        self.getToken()
        self.quote  = None
        self.headers = None
        self.set_header()
        



    def login(self):
        
        json = {
            "secretKey":self.secretKey,
            "appKey":self.appKey,
            "source":self.source
        }

        r = requests.post(self.baseurl+self.loginpath, json = json)
        if self.checkresponse(r):
            print("Login successful")
            self.token = r.json()['result']['token']
            self.set_header()


    def checkresponse(self, response):
        if response.status_code!=200:
            # print("Error",response.json()['description'])
            print(response.text)
            return 0
        else:
            return 1

    def getsymbol(self, esegment, series, symbol):
        self.getsymbolurl = "/instruments/instrument/symbol?"
        
        r = requests.get(self.baseurl+self.getsymbolurl+f"exchangeSegment={esegment}&series={series}&symbol={symbol}")
        if self.checkresponse(r):
            data = r.json()
            self.instrument_id = data['result'][0]['ExchangeInstrumentID']
            # print("ID {}".format(data['result'][0]['ExchangeInstrumentID']))
            return self.instrument_id
            

    def get_quote(self, esegment=1, xts=1502, publish='JSON'):
        
        json = {
            "instruments":[
                {
                
                "exchangeSegment":esegment,
                "exchangeInstrumentID":self.instrument_id
            }
            ],

            "xtsMessageCode": xts,
            "publishFormat" : publish
        }

        r = requests.post(self.baseurl+self.getquoteurl,json = json,headers = self.headers)
        if(self.checkresponse(r)):
            # print(r.json())
            self.quote = eval(r.json()['result']['listQuotes'][-1])
            # self.quote = r.json()
            print(r.json())
        else:
            return

        self.low = self.quote["Touchline"]['Low']
        self.high = self.quote['Touchline']['High']
        self.close = self.quote['Touchline']['Close']
        self.totaltraded = self.quote['Touchline']['TotalValueTraded']
        self.open = self.quote['Touchline']['Open']
        self.bidinfo = self.quote['Touchline']['BidInfo']
        self.askinfo = self.quote['Touchline']['AskInfo']
        self.avgprice = self.quote['Touchline']['AverageTradedPrice']
        return (self.low, self.high, self.open, self.close)

    def getToken(self):
        file = self.file
        with open(file,'r+') as fp:
            data = fp.read()
            if(len(data)<=2):
                print(len(data),data)
                self.login()

                fp.write(self.token)
            else:
                self.token = data

        return self.token


    def set_header(self):
        self.headers = {
            "Content-Type":"application/json",
            "authorization":self.token
        }

    
class IApi(MarketApi):
    def __init__(self):
        super().__init__()
        self.place_order_url = "/interactive/orders"
        self.baseurl = "https://ttblaze.iifl.com"
        self.mod_order = None
        self.cid = None
        self.token = None
        self.file = "token2.txt"
        self.loginpath = "/interactive/user/session"
        self.secretKey = str(os.getenv("isecretKey"))
        self.appKey = str(os.getenv("iappKey"))
        self.source = str(os.getenv("isource"))
        self.getToken()
        self.generate_cid()
        self.orderid = None

    def getToken(self):
        file = self.file
        with open(file,'r+') as fp:
            data = fp.read()
            if(len(data)<=2):
                print(len(data),data)
                self.login()
                fp.write(self.token)
                f = open("clientID.txt","r+")
                f.write(self.cid)
                f.close()
            else:
                self.token = data

        return self.token
        
        
    def place_order(self, esegment= "NSECM", eid=3045, ptype = "NRML",otype="LIMIT", oslide="BUY", tinforce="DAY", quantity=1, lprice = 10, ouid='123abc'):
        json = {

            "clientID": self.cid,
            "exchangeSegment": "NSECM",
            "exchangeInstrumentID": eid,
            "productType": ptype,
            "orderType": otype,
            "orderSide": oslide,
            "timeInForce": tinforce,
            "disclosedQuantity": 1,
            "orderQuantity": 1,
            "limitPrice": 254.55,
            "stopPrice": 0,
            "orderUniqueIdentifier": "123xyz"
        }
        print(json)
        r = requests.post(self.baseurl+self.place_order_url,json=json,headers=self.headers)
        if (self.checkresponse(r)):
            data  = r.json()
            self.orderid = data['result']['AppOrderID']
            print("Status : %s"%data['type'])
    
    def login(self):
        json = {
            "secretKey":self.secretKey,
            "appKey":self.appKey,
            "source":self.source
        }

        r = requests.post(self.baseurl+self.loginpath, json = json)
        if self.checkresponse(r):
            print("Login successful")
            data = r.json()
            print(data)
            self.token = data['result']['token']
            self.set_header()
            self.cid = data['result']['clientCodes'][0]
            self.userid = data['result']['userID']
            self.isInvestorClient = data['result']['isInvestorClient']
        
            
    def generate_cid(self):
        with open("clientID.txt","r+") as fp:
            data = fp.read()
            if(len(data)<1):
                self.login()
                fp.write(self.cid)

            else:
                self.cid = data
