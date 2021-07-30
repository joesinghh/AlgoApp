from kite_api import Kite
from ifl_api import MarketApi

class AdapterApi(object):
    def __init__(self, cls):
        self.cls = cls
        if isinstance(self.cls,MarketApi):
            self.value = 1
        else:
            self.value = 0

    def place_order():
        pass
    
    

