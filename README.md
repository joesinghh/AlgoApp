## AlgoApp - Algo trading desktop application.

<!-- [![GitHub](https://img.shields.io/github/license/Joe-Sin7h/AlgoApp)]() -->

Application makes use of several APIs like IFL api, Zerodha paid api and Zerodha free api. For using the application user must have demat account on anyone of these platforms (i.e **IFL** or **Zerodha** ). 

![](https://raw.githubusercontent.com/Joe-Sin7h/AlgoApp/main/application.JPG?raw=true)
### Installation

Install dependencies:

```pip install -r requirements.txt```


Run application : 

```python main.py```

### Set-Up keys
`ifl.json`
```Json
{
    "marketdata":{
        "secretKey" : "<your IFL secret key>",
        "appKey" : "<you app key>",
        "source" : "WEBAPI"
    },

    "interactive":{
        "secretKey" : "<your IFL secret key>",
        "appKey" : "<you app key>",
        "source" : "WEBAPI"
    }
    
}
```
Adding API key in `kite.json` is not necessary if you want place order using kite free api.
```Json
{
    "kitekey":"<kite api key (paid api)>"
}
```
`kitefree.json`
```Json
{
    "userid":"<you kite userid>",
    "password":"<your kite login password>",
    "twofa":"<2 factor authentication>"
}
```
### Notes on usage

- Add suitable API Keys in `/Config`.
- Login from Application.
- Place Orders.
