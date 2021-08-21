import requests

header = {
    'Content-Type':'application/x-www-form-urlencoded',
    'Authorization':'enctoken scAgwhH0V0ObRnwDGYhVMooHcIQE6QCAP6QUZA9lNT8TNbQHS0VA2dvRMl5gTjVrFmzzz7/g1ZePrTWaZm3VzzOhN9y94PwaNe14wjmXT8rTdlxhLHwpaQ=='
}

def place_enc_order(tradingsymbol="", tt='BUY',ot="MARKET" ,q=1,dsq=1,exch="NSE",product="Normal"):
    data = {
        'tradingsymbol':tradingsymbol,
        'transaction_type':tt,
        'order_type':ot,
        'quantity':q,
        'disclosed_quantity':dsq,
        'exchange':"NSE",
        'product':product
    }

    data = "tradingsymbol=FSL&transaction_type=BUY&order_type=MARKET&quantity=1&disclosed_quantity=1&exchange=NSE&product=MIS"

    print(data)
    r = requests.post('https://kite.zerodha.com/oms/orders/regular',data=data,headers=header,verify=False)
    print(r.json())
    print(r.status_code)


place_enc_order()


