import logging
import requests
from dotenv import load_dotenv
import json
import logging.config

logging.config.fileConfig('.\\Logs\\log.ini',disable_existing_loggers=False)
logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
load_dotenv()
null = 0
false = False
true = True


class MarketApi(object):

    def __init__(self):
        f = open(".\\Config\\ifl.json")
        self.data = json.load(f)
        self.secretKey = self.data['marketdata']["secretKey"]
        self.appKey = self.data['marketdata']["appKey"]
        self.source = self.data['marketdata']["source"]
        self.isecretKey = self.data['interactive']["secretKey"]
        self.iappKey = self.data['interactive']["appKey"]
        self.isource = self.data['interactive']["source"]

        self.instrument_id = None
        self.series = None
        self.cid = None
        self.file  = ".\\Tokens\\token.txt"
        self.file2 = ".\\Tokens\\token2.txt"
        self.placeurl = "/interactive/orders"
        self.baseurl_place = "https://ttblaze.iifl.com"
        self.baseurl = "https://ttblaze.iifl.com/apimarketdata"
        self.getquoteurl = "/instruments/quotes"
        self.loginpath = "/auth/login"
        self.loginpath2 = "/interactive/user/session"
        self.orderid = None
        self.expath = "/instruments/instrument/expiryDate"
        self.token = None
        self.tokeni = None
        self.getToken()
        self.getTokeni()
        self.generate_cid()
        self.quote  = None
        self.headers = None
        self.headersi = None
        self.set_headeri()
        self.set_header()

    def getTokeni(self):
        file = self.file2
        with open(file,'r+') as fp:
            data = fp.read()
            if(len(data)<=2):
                self.logini()
                fp.write(self.tokeni)
                f = open(".\\Tokens\\clientID.txt","r+")
                f.write(self.cid)
                f.close()
            else:
                self.tokeni = data

        return self.tokeni

    def logini(self):
        json = {
            "secretKey":self.isecretKey,
            "appKey":self.iappKey,
            "source":self.isource
        }

        r = requests.post(self.baseurl_place+self.loginpath2, json = json)
        if self.checkresponse(r):
            data = r.json()
            self.tokeni = data['result']['token']
            self.set_headeri()
            self.cid = data['result']['clientCodes'][0]
            self.userid = data['result']['userID']
            self.isInvestorClient = data['result']['isInvestorClient']
            with open(self.file2,'w') as f:
                f.write(self.tokeni)
        
    def generate_cid(self):
        with open(".\\Tokens\\clientID.txt","r+") as fp:
            data = fp.read()
            if(len(data)<1):
                self.login()
                fp.write(self.cid)
            else:
                self.cid = data
                
    def login(self):
        
        json = {
            "secretKey":self.secretKey,
            "appKey":self.appKey,
            "source":self.source
        }

        r = requests.post(self.baseurl+self.loginpath, json = json)
        if self.checkresponse(r):
            
            self.token = r.json()['result']['token']
            with open(self.file,"w") as f:
                f.write(self.token)

            self.set_header()

    def checkresponse(self, response):
        if response.status_code!=200:
            # print(response.text)
            # print(response.status_code)
            return 0
        else:
            return 1

    def get_symbol(self, esegment, series, symbol):
        self.getsymbolurl = "/instruments/instrument/symbol?"
        
        r = requests.get(self.baseurl+self.getsymbolurl+f"exchangeSegment={esegment}&series={series}&symbol={symbol}")
        if self.checkresponse(r):
            data = r.json()
            self.lotsize = data['result'][-1]['LotSize']
            self.instrument_id = data['result'][0]['ExchangeInstrumentID']
            return self.instrument_id,self.lotsize
            
    def get_quote(self,instrument_id, esegment=1, xts=1504, publish='JSON',):
        
        json = {
            "instruments":[
                {
                
                "exchangeSegment":esegment,
                "exchangeInstrumentID":instrument_id
            }
            ],

            "xtsMessageCode": xts,
            "publishFormat" : publish
        }

        r = requests.post(self.baseurl+self.getquoteurl,json = json,headers = self.headers)
        if(self.checkresponse(r)):
            try:

                self.quote = eval(r.json()['result']['listQuotes'][0])
            except Exception as e:
                logging.error(e,exc_info=True)
                print(e)
            
            self.bids = [self.quote['Bids'][0]['Price'],self.quote['Bids'][1]['Price'],self.quote['Bids'][2]['Price']]
            self.asks = [self.quote['Asks'][0]['Price'],self.quote['Asks'][1]['Price'],self.quote['Asks'][2]['Price']]
            # print(f"{instrument_id} BUY",self.bids[0])
            # print(f"{instrument_id} SELL",self.asks[0])
            return self.bids, self.asks

        else:
            logging.error(r.text)
            print(r.text)

       
    def getToken(self):
        file = self.file
        with open(file,'r+') as fp:
            data = fp.read()
            if(len(data)<=2):

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
    def set_headeri(self):
        self.headersi = {
            "Content-Type":"application/json",
            "authorization":self.tokeni
        }

    def get_expiry(self,symbol, esegment=2, series='OPTIDX'):

        r = requests.get(self.baseurl+self.expath+f"?exchangeSegment={esegment}&series={series}&symbol={symbol}",verify=False)
        if self.checkresponse(r):
            self.listexp = [date.split("T")[0] for date in  list(r.json()['result'])]
            
            return self.listexp

        else:
            print(r.text)
            return None

    def get_option_symbol(self,symbol,expirydate,otype,sprice,series,esegment=2):
        data = {
            "exchangeSegment":esegment,
            "series":series,
            "symbol":symbol,
            "expiryDate":expirydate,
            "optionType":otype,
            "strikePrice":sprice
        }
        
        # print(f"{esegment} &series={series} &symbol={symbol} &expiryDate={expirydate} &optionType={otype} &strikePrice={sprice}")
        r = requests.get(self.baseurl+f"/instruments/instrument/optionSymbol?exchangeSegment={esegment}&series={series}&symbol={symbol}&expiryDate={expirydate}&optionType={otype}&strikePrice={sprice}")
        if self.checkresponse(r):
            rdata = r.json()['result'][0]

            lot_size = rdata['LotSize']
            self.instrument_id = rdata['ExchangeInstrumentID']

            return lot_size, self.instrument_id

        else:
            
            return None, None
    def place_order(self,eid=3045, oslide="SELL" , quantity=1, ouid='',*args):
        json = {

            "clientID": self.cid,
            "exchangeSegment": "NSEFO",
            "exchangeInstrumentID": eid,
            "productType": "NRML",
            "orderType": "MRKT",
            "orderSide": oslide,
            "timeInForce": "DAY",
            "disclosedQuantity": 1,
            "orderQuantity": quantity,
            "limitPrice": 254.55,
            "stopPrice": 0,
            "orderUniqueIdentifier": "123abc"
        }
        r = requests.post(self.baseurl_place+self.placeurl,json=json,headers=self.headers)
        data  = r.json()

        if (self.checkresponse(r)):
            self.orderid = data['result']['AppOrderID']
            # print("Status : %s"%data['type'])
        elif r.status_code<500:
            raise Exception(data['data']['description'])
        else:
            raise Exception("Server Error!")

