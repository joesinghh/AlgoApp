from datetime import datetime
from dateutil.relativedelta import relativedelta, TH

list_of_months = {1: 'Jan', 2: 'Feb', 3: 'Mar',
                4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul',
                8: 'Aug', 9: 'Sep', 10: 'Oct',
                11: 'Nov', 12: 'Dec'
            } 

def convert_date(date):
    """
    Change format of a date from `%d-%m-%Y %b`
    to `%d%b%Y`.
    example : 19-09-2021 Sep -> 19Sep2021

    Returns
    -------
    datetime.date
        Date object with changed format.
    """
    date = datetime.strptime(date,"%d-%m-%Y %b").date()
    date = date.strftime("%d%b%Y")
    return date
                         
def check_if_last(date):
    exdate = datetime.date(datetime.strptime(date,"%d%b%Y"))
    exmonth = exdate.month
    exday = exdate.day

    for i in range(1, 6):
        t = exdate + relativedelta(weekday=TH(i))
        if t.month!=exmonth:
            t = t + relativedelta(weekday=TH(-2))
            break

    return exday==t.day

def exchange_name(instru, expiry, strike_price, call):
    
    if type(strike_price)!=str:
        strike_price = str(strike_price)
    # print("EXPIRY ",expiry)
    date = datetime.date(datetime.strptime(expiry,"%d%b%Y"))
    year = str(date.year)
    month = date.month
    day = date.day
    day_ = "0"+str(day) if day>0 and day<10 else str(day)
    month_ = list_of_months[month][0].upper() if month>9 else str(month)
    
    # print(date, year, month,)
    if check_if_last(expiry) and month<10:
        ex = instru+year[-2:]+list_of_months[date.month].upper()+strike_price+call
    else:
        ex = instru+year[-2:]+month_+day_+strike_price+call
        
    return ex

if __name__=='__main__':

    exchange_name("NIFTY","07Aug2021","23444","PE")

