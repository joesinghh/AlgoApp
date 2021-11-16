from kite_api import Kite
from tkinter import *
from threading import Thread, Lock
from ifl_api import MarketApi
from tkinter import messagebox
import pandas as pd
from datetime import datetime
from handlefile import delete_data, fetch_data, insert_data, fetch_data, change_data
from Auto import AutocompleteCombobox
import platform
import time
import xlrd
from Adapter import AdapterApi
from exchange import exchange_name, convert_date
import logging.config
import traceback

logging.config.fileConfig(r'.\Logs\log.ini',disable_existing_loggers=False)
logging.getLogger(__name__)

   
BUY = "BUY"
SELL = "SELL"
EXIT_ALL = 0 

#Milisecconds 
CALL_FEQ = 10000
NEW_CALL_FEQ = 3000

#Seconds
TARGETDIFF = 3
SLDIFF = 3

try:
    dataframe = pd.read_excel(".\\OrderData\\order_data.xlsx")
    pending_df = pd.read_excel('.\\OrderData\\notcompleted.xlsx')
    completed_df = pd.read_excel('.\\OrderData\\completed.xlsx')
except:
    logging.error("Exception: %s", traceback.format_exc())

try :
    last_num = dataframe['SN'].iloc[-1]
except IndexError as e:
    last_num = 1
    logging.error(e, exc_info=True)

try : 
    last_cnum = dataframe['SN'].iloc[-1]
except IndexError as e:
    last_cnum = 1
    logging.error(e, exc_info=True)

columns = dataframe.columns

trade_threads  = 0
y_value = 100

mp = MarketApi()
lock = Lock()
#variables to control threads
price_thread1 = 0
price_thread2 = 0
price_thread3 = 0
price_thread4 = 0

lsize_thread1 = 0
lsize_thread2 = 0
lsize_thread3 = 0
lsize_thread4 = 0

isop_thread = 0

PlaceOrderClass = AdapterApi(None) #Adapter Class

class ScrollFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.
            
        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            # self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
            pass
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")


def exit_all_trade():
    """
    Exit all Trade at a given moment.
    All trades will be squared off.
    """
    global EXIT_ALL
    mssg = messagebox.askyesno("EXIT","Do you want to exit all orders ?")
    if mssg:
        EXIT_ALL  = 1

    
def clear_order_variables():
    """
    Clear OrderScreen variables and set new values.
    """
    product_type.set("MIS")
    bs1.set(None)
    bs2.set(None)
    bs3.set(None)
    bs4.set(None)

    instru1.set("")
    instru2.set("")
    instru3.set("")
    instru4.set("")

    otype1.set(None)
    otype2.set(None)
    otype3.set(None)
    otype4.set(None)

    expiry1.set("")
    expiry2.set("")
    expiry3.set("")
    expiry4.set("")

    price1.set(0)
    price2.set(0)
    price3.set(0)
    price4.set(0)

    l1.set(0)
    l2.set(0)
    l3.set(0)
    l4.set(0)

    lotdata1.set("")
    lotdata2.set("")
    lotdata3.set("")
    lotdata4.set("")

    premium1.set(0)
    premium2.set(0)
    premium3.set(0)
    premium4.set(0)

    
def clear():
    """
    Clear PlaceOrder screen variables and assign new values.
    """
    global price_thread1, price_thread2, price_thread3, price_thread4,\
        lsize_thread1, lsize_thread2, lsize_thread3, lsize_thread4

    ls.set(-1)
    cp.set(-1)
    st1.set(0)
    st2.set(0)
    st3.set(0)
    st4.set(0)
    # instrument.set("")
    instu.set("")
    
    lots.set(1)
    expiry.set("")
    Bid_label['text'] = "None"
    Ask_label['text'] = "None"
    inable_all()

    price_thread1 = 0
    price_thread2 = 0
    price_thread3 = 0
    price_thread4 = 0

    lsize_thread1 = 0
    lsize_thread2 = 0
    lsize_thread3 = 0
    lsize_thread4 = 0
    


def preorderscreen():
    clear()
    preorderframe.tkraise()

def orderscreen():
    orderframe.tkraise()

def ordermenuscreen():
    """
    Start Threads in OrderScreen.
    """
    global price_thread1, price_thread2, price_thread3, price_thread4, lsize_thread1, lsize_thread2, lsize_thread3, lsize_thread4
    lsize_thread1, lsize_thread2, lsize_thread3, lsize_thread4 = 1, 1, 1, 1
    price_thread1, price_thread2, price_thread3, price_thread4 = 1, 1, 1, 1
    
    clear_order_variables()
    owidget_active()
    update_price_label()
    update_lotlabel()
    orderframe.tkraise()


def getexpiry():
    """
    get list of expiry date from IFL api.

    Returns
    -------
    list 
        sorted list of expiry dates in `%d-%m-%Y %b` format.
    """
    symbol = "NIFTY"

    s = "OPTSTK"
    if "NIFTY" in symbol:
        s = "OPTIDX"

    dates = mp.get_expiry(symbol=symbol,esegment=2,series=s)
    date = []

    for  i in dates:
        d = datetime.strptime(i,"%Y-%m-%d").date()
        date.append(str(d.strftime("%d-%m-%Y %b")))

    date.sort()
    date = sorted(date,key=lambda x: x.split("-")[1])    
    date = sorted(date,key=lambda x: x.split("-")[2].split(" ")[0])    
    return date


def inable_all():
    """
    Inable all Strike price widgets in PlaceOrder Screen.
    """
    strike = [s1,s2,s3,s4]
    for i in strike:
        i['state'] = 'normal'

def disable_n(n):
    """
    Parameters
    ----------
    n : int
        int specifing how many stike price widgets on PlaceOrder
        Screen will be disabled.
    """
    strike = [s4,s3,s2,s1]

    for i in range(1,n+1):
        strike[i-1]['state'] = 'disable'


def dummy_radio_fun():
    t = Thread(target=radio_fun)
    t.start()

def radio_fun():
    """
    Function called by radiobuttons to disable/inable
    Strike price Widgets on PlaceOrder screen based on a strategy.
    """
    value = cp.get()
    if value!=-1:
        inable_all()
        if cp.get() in [1,2,3]:
            disable_n(2)
        elif cp.get() ==4:
            disable_n(1)

def setorder():
    """
    Function to validate input and open OrderScreen
    for placing orders.
    """
    if cp.get()==-1 or  ls==-1:
        messagebox.showerror("ERROR","Select a Valid Strategy")
        return 0

    try:
        if lots.get() <=0 :
            messagebox.showerror("ERROR","Invalid Lot Size")
    except Exception as e:
        messagebox.showerror("ERROR",e+" for Lot No.")
        logging.error(e,exc_info=True)
        return 0
        
    else:
        clear_order_variables() # Clears orderscreen variables.
        update_order(cp.get()) # Update orderscreen variables.
        orderscreen()


def start_setorder():
    t = Thread(target=setorder)
    t.start()

def update_order(n):
    """
    Function to manage Order Blocks on orderscreen and their 
    threads for updating marketprice and lotsize.

    Parameters
    ----------
    n : int
        int specifying number of order instruments to manage.
        This number depends on the strategy choosen on placeorder screen. 
    """
    global price_thread1, price_thread2, price_thread3, price_thread4, lsize_thread1, lsize_thread2, lsize_thread3, lsize_thread4,\
    isop_thread

    instru_value  = instu.get()
    expiry_date = expiry.get()
    api_expiry_date = convert_date(expiry_date)
    lots_num = lots.get()
    isop_thread = 1
    s = "OPTSTK"

    if instru_value.find("NIFTY")!=-1:
        s = "OPTIDX"

    if n in [1,2,3]:
        owidget_active()
        owidget_disable(2)
        s1instru.set(instru_value)
        s2instru.set(instru_value)

        l1.set(lots_num)
        l2.set(lots_num)

        if ls.get()==1:
            bs1.set(BUY)
            bs2.set(SELL)

        else:
            bs1.set(SELL)
            bs2.set(BUY)

        
        if n==2:
            otype1.set("PE")
            otype2.set("PE")
        else:
            otype1.set("CE")
            otype2.set("CE")
        


        num1, _ = get_instru_id(instru_value,"CE",api_expiry_date,st1.get(),s)
        num2  = num1

        lotdata1.set(str(num1))
        lotdata2.set(str(num2))

        price1.set(st1.get())
        price2.set(st2.get())
        
        price_thread1 = 1
        price_thread2 = 1

        lsize_thread1 = 1
        lsize_thread2 = 1
        expiry1.set(expiry_date)
        expiry2.set(expiry_date)


    elif n==4:
        owidget_active()
        owidget_disable(1)

        s1instru.set(instru_value)
        s2instru.set(instru_value)
        s3instru.set(instru_value)


        l1.set(lots_num)
        l2.set(lots_num)
        l3.set(lots_num)

        if ls.get()==1:
            bs1.set(BUY)
            bs2.set(SELL)
            bs3.set(BUY)

        else:
            bs1.set(SELL)
            bs2.set(BUY)
            bs3.set(SELL)

        otype1.set("CE")
        otype2.set("CE")
        otype3.set("CE")

        num1, _ = get_instru_id(instru_value,"CE",api_expiry_date,st1.get(),s)
        num2 = num1
        num3 = num1
        
        lotdata1.set(str(num1))
        lotdata2.set(str(num2))
        lotdata3.set(str(num3))
        
        price1.set(st1.get())
        price2.set(st2.get())
        price3.set(st3.get())

        #Start Threads
        price_thread1 = 1
        price_thread2 = 1
        price_thread3 = 1

        lsize_thread1 = 1
        lsize_thread2 = 1
        lsize_thread3 = 1
        expiry1.set(expiry_date)
        expiry2.set(expiry_date)
        expiry3.set(expiry_date)

    else:
        owidget_active()


        s1instru.set(instru_value)
        s2instru.set(instru_value)
        s3instru.set(instru_value)
        s4instru.set(instru_value)


        l1.set(lots_num)
        l2.set(lots_num)
        l3.set(lots_num)
        l4.set(lots_num)
        num1, _ = get_instru_id(instru_value,"PE",api_expiry_date,st1.get(),s)
        num2, _ = get_instru_id(instru_value,"CE",api_expiry_date,st2.get(),s)


        if ls.get()==1:
            bs1.set(BUY)
            bs2.set(SELL)
            bs3.set(BUY)
            bs4.set(SELL)


        else:
            bs1.set(SELL)
            bs2.set(BUY)
            bs3.set(SELL)
            bs4.set(BUY)

        otype1.set("CE")
        otype2.set("CE")
        otype3.set("PE")
        otype4.set("PE")

        lotdata1.set(str(num1))
        lotdata2.set(str(num1))
        lotdata3.set(str(num2))
        lotdata4.set(str(num2))

        price1.set(st1.get())
        price2.set(st2.get())
        price3.set(st3.get())
        price4.set(st4.get())

        #Start Threads
        price_thread1 = 1
        price_thread2 = 1
        price_thread3 = 1
        price_thread4 = 1

        lsize_thread1 = 1
        lsize_thread2 = 1
        lsize_thread3 = 1
        lsize_thread4 = 1

        expiry1.set(expiry_date)
        expiry2.set(expiry_date)
        expiry3.set(expiry_date)
        expiry4.set(expiry_date)

    update_thread = Thread(target=update_price_label,args=())
    update_thread.start()
    update_lotlabel()

    
def owidget_disable(n):
    """
    Disable Widgets on OrderScreen.
    """
    for i in range(n):
        list_sc[i]['state'] = 'disable'
        list_sp[i]['state'] = 'disable'
        list_b[i]['state'] = 'disable'
        list_s[i]['state'] = 'disable'
        list_exp[i]['state'] = 'disable'
        list_instru[i]['state'] = 'disable'
        list_lotlabel[i]['state'] = 'disable'
        list_sprice[i]['state'] = 'disable'
        list_mkprice[i]['state'] = 'disable'
        list_lot[i]['state'] = 'disable'
    

def owidget_active():
    """
    Activate Widgets on OrderScreen.
    """
    for i in range(4):
        list_sc[i]['state'] = 'normal'
        list_sp[i]['state'] = 'normal'
        list_b[i]['state'] = 'normal'
        list_s[i]['state'] = 'normal'
        list_exp[i]['state'] = 'normal'
        list_instru[i]['state'] = 'normal'
        list_lotlabel[i]['state'] = 'normal'
        list_sprice[i]['state'] = 'normal'
        list_mkprice[i]['state'] = 'normal'
        list_lot[i]['state'] = 'normal'


def set_top():
    """
    Create TradeManagement Screen.
    """
    global top, scroll_frame, display_frame

    top = Toplevel()
    scroll_frame = ScrollFrame(top)
    scroll_frame.pack(fill='both',expand=1)
    scroll_frame.tkraise()
    display_frame = Frame(scroll_frame.viewPort,bg='white')
    display_frame.pack(side='top',anchor=NW,fill='both',expand=1)
    display_frame.tkraise()
    trade_frame = Frame(display_frame,bg='white')
    trade_frame.pack(fill='x',expand=1,ipady=100)
    trade_frame.tkraise()

    top.geometry('700x600')
    top.resizable(0,0)
    top.title("AlgoApp | Trade Management")
    top.withdraw()

    top.protocol('WM_DELETE_WINDOW',top.withdraw)  # Replace default close function
    Label(display_frame,text='Initial SOP',font=('Calibri',13),bg='white').place(x=30,y=20)
    Label(trade_frame,text='Current SOP',font=('Calibri',13),bg='white').place(x=170,y=20)
    Label(trade_frame,text='Target',font=('Calibri',13),bg='white').place(x=310,y=20)
    Label(trade_frame,text='SL',font=('Calibri',13),bg='white').place(x=410,y=20)
    Label(trade_frame,text='P&L',font=('Calibri',13),bg='white').place(x=510,y=20)

def tradescreen():
    """
    Open TradeManagement Screen.
    """
    top.deiconify()


def create_api_top():
    """
    Create API selction window for placing
    orders. Default api for placing orders 
    is `Kite Free`.
    """
    global api_variable, api_top
    api_top = Toplevel(bg='white')
    api_top.geometry('200x200')
    api_top.resizable(0,0)
    api_variable = IntVar()
    api_variable.set(3)
    
    Label(api_top,text=" Select You API for placing orders. ",font=("Arial",9,"bold"),bg='white').pack(pady=12)
    ifl = Radiobutton(api_top,text="IFL",variable=api_variable,value=1,bg='white',command=set_Adapter)
    ifl.pack(pady=10)

    kite_api = Radiobutton(api_top,text='Kite',variable=api_variable,value=2,bg='white',command=set_Adapter)
    kite_api.pack(pady=10)

    kite_free = Radiobutton(api_top,text='Kite Free',variable=api_variable,value=3,bg='white',command=set_Adapter)
    kite_free.pack(pady=10)

    api_top.withdraw()
    api_top.protocol('WM_DELETE_WINDOW',api_top.withdraw)

def order_api():
    """
    Open API Selection window.
    """
    api_top.deiconify()

def set_Adapter():
    """
    Change Adapter based on the API selection 
    for placing orders on API selection screen.
    """
    global PlaceOrderClass
    if api_variable.get()==1:
        PlaceOrderClass = AdapterApi(MarketApi())
    # elif api_variable.get()==2:
    #     PlaceOrderClass = AdapterApi(Kite())
    elif api_variable.get()==3:
        PlaceOrderClass = AdapterApi(None)

    
def dummy_place_order():
    t = Thread(target=place_realorder)
    t.start()
    
def update_price_label():
    """
    Function to start Threads for updating market price
    of instruments in OrderScreen.
    """
    price_thread_list = [price_thread1, price_thread2,price_thread3, price_thread4]
    if price_thread_list.count(1)==2:
        t1 = Thread(target=price_update_thread1,args=())
        t1.start()
        t2 = Thread(target=price_update_thread2,args=())
        t2.start()
        
    elif price_thread_list.count(1)==3:
        t1 = Thread(target=price_update_thread1,args=())
        t1.start()
        t2 = Thread(target=price_update_thread2,args=())
        t2.start()
        t3 = Thread(target=price_update_thread3,args=())
        t3.start()

    elif price_thread_list.count(1)==4:
        t1 = Thread(target=price_update_thread1,args=())
        t1.start()
        t2 = Thread(target=price_update_thread2,args=())
        t2.start()
        t3 = Thread(target=price_update_thread3,args=())
        t3.start()
        t4 = Thread(target=price_update_thread4,args=())
        t4.start()
    t5 = Thread(target=update_isop,args=())
    t5.start()

def price_update_thread1():
    """
    Function to Update market Price of 1st
    instrument in OrderScreen.
    """
    if instru1.get() and otype1.get():
         
        o = 'CE'
        if otype1.get()=="PE":
            o = "PE"
        instru = instru1.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            _, id_ = get_instru_id(instru,o,convert_date(expiry1.get()),price1.get(),series)
            m  = MarketApi()
            m_bid, m_ask = m.get_quote(id_,2,1502)
            
            if bs1.get()==BUY:
                premium1.set(float(m_ask[0]))
            else:
                premium1.set(float(m_bid[0]))

        except Exception as e:
            print("price update 1 ",e)
            logging.error(e,exc_info=True)

    if price_thread1:
        time.sleep(5)
        price_update_thread1()
    else:
        return

def price_update_thread2():
    """
    Function to Update market Price of 2nd
    instrument in OrderScreen.
    """
    
    if instru2.get() and otype2.get():


        o = 'CE'
        if otype2.get()=="PE":
            o = "PE"

        instru = instru2.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            _, id_ = get_instru_id(instru,o,convert_date(expiry2.get()),price2.get(),series)
            m  = MarketApi()
            m_bid, m_ask = m.get_quote(id_,2,1502)
            if bs2.get()==BUY:
                premium2.set(str(m_ask[0]))
            else:
                premium2.set(str(m_bid[0]))

        except Exception as e:
            print("price update 2 ",e)
            logging.error(e,exc_info=True)

    if price_thread2:
        time.sleep(5)
        price_update_thread2()
    else:
        return

def price_update_thread3():
    """
    Function to Update market Price of 3rd
    instrument in OrderScreen.
    """
    if instru3.get() and otype3.get():

        o = 'CE'
        if otype3.get()=="PE":
            o = "PE"
        instru = instru3.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            _, id_ = get_instru_id(instru,o,convert_date(expiry3.get()),price3.get(),series)
            m  = MarketApi()
            m_bid, m_ask = m.get_quote(id_,2,1502)
            if bs3.get()==BUY:
                premium3.set(str(m_ask[0]))
            else:
                premium3.set(str(m_bid[0]))

        except Exception as e:
            print("price update 3 ",e)
            logging.error(e,exc_info=True)


    if price_thread3:
        time.sleep(5)
        price_update_thread3()
    else:
        return

def price_update_thread4():
    """
    Function to Update market Price of 4th
    instrument in OrderScreen.
    """
    if instru4.get():

        o = 'CE'
        if otype4.get()=="PE":
            o = "PE"

        instru = instru4.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            _, id_ = get_instru_id(instru,o,convert_date(expiry4.get()),price4.get(),series)
            m  = MarketApi()
            m_bid, m_ask = m.get_quote(id_,2,1502)

            if bs4.get()==BUY:
                premium4.set(str(m_ask[0]))
            else:
                premium4.set(str(m_bid[0]))

        except Exception as e:
            print("price update 4 ",e)
            logging.error(e,exc_info=True)


    if  price_thread4:
        time.sleep(5)
        price_update_thread4()
    else:
        return

def update_isop():

    try:

        bs = [bs1.get(), bs2.get(), bs3.get(), bs4.get()]
        lots = [l1.get(), l2.get(), l3.get(), l4.get()]
        price_list = [premium1.get(), premium2.get(), premium3.get(), premium4.get()]
        isop = 0
        for i in range(4):
            if bs[i]=="BUY":
                isop+=(lots[i]*price_list[i])
            elif bs[i]=="SELL":
                isop-=(lots[i]*price_list[i])

        isop_value['text'] = f'{isop:.2f}'
    except Exception as e:
        logging.error(e,exc_info=True)
        
    if isop_thread:
        time.sleep(4.9)
        update_isop()
    else:
        return


def update_lotlabel():
    """
    Function to start Threads for updating lot size
    of instruments in OrderScreen.
    """
    lot_label_list = [lsize_thread1, lsize_thread2, lsize_thread3,lsize_thread4]

    if lot_label_list.count(1)==2:
        t1 = Thread(target=set_lot_label1,args=())
        t1.start()
        t2 = Thread(target=set_lot_label2,args=())
        t2.start()

    elif lot_label_list.count(1)==3:
        t1 = Thread(target=set_lot_label1,args=())
        t1.start()
        t2 = Thread(target=set_lot_label2,args=())
        t2.start()
        t3 = Thread(target=set_lot_label3,args=())
        t3.start()

    elif lot_label_list.count(1)==4:
        t1 = Thread(target=set_lot_label1,args=())
        t1.start()
        t2 = Thread(target=set_lot_label2,args=())
        t2.start()
        t3 = Thread(target=set_lot_label3,args=())
        t3.start()
        t4 = Thread(target=set_lot_label4,args=())
        t4.start()


def set_lot_label1():
    """
    Function to Update lot size of 1st
    instrument in OrderScreen.
    """
    if instru1.get() and exp1['value']:
        o = 'CE'
        if otype1.get()=="PE":
            o = "CE"

        instru = instru1.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            lotsize, id_ = get_instru_id(instru,o,convert_date(expiry1.get()),price1.get(),series)
            lotdata1.set(str(lotsize))
        except Exception as e:
            print("Lot size 1 ",e)
            logging.error(e,exc_info=True)

    if lsize_thread1:
        time.sleep(5)
        set_lot_label1()
    else:
        return

def set_lot_label2():
    """
    Function to Update lot size of 2nd
    instrument in OrderScreen.
    """
    if instru2.get() and exp2['value']:
        o = 'CE'
        if otype2.get()=="PE":
            o = "PE"
        instru = instru2.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            lotsize, id_ = get_instru_id(instru,o,convert_date(expiry2.get()),price2.get(),series)
            lotdata2.set(str(lotsize))
        except Exception as e:
            print("lot size 2 ",e)
            logging.error(e,exc_info=True)

    if lsize_thread2:
        time.sleep(5)
        set_lot_label2()
    else:
        return

def set_lot_label3():
    """
    Function to Update lot size of 3rd
    instrument in OrderScreen.
    """
    if instru3.get() and exp3['value']:
        o = 'CE'
        if otype3.get()=="PE":
            o =  "PE"

        instru = instru3.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            lotsize, id_ = get_instru_id(instru,o,convert_date(expiry3.get()),price3.get(),series)
            lotdata3.set(str(lotsize))
        except Exception as e:
            print("lot size 3 ",e)
            logging.error(e,exc_info=True)

    if lsize_thread3:
        time.sleep(5)
        set_lot_label3()
    else:
        return

def set_lot_label4():
    """
    Function to Update lot size of 4th 
    instrument in OrderScreen.
    """
    if instru4.get() and exp4['value']:
        o = 'CE'
        if otype4.get()=="PE":
            o = "PE"

        instru = instru4.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            lotsize, id_ = get_instru_id(instru,o,convert_date(expiry4.get()),price4.get(),series)
            lotdata4.set(str(lotsize))
        except Exception as e:
            print("lot size 4 ",e)
            logging.error(e,exc_info=True)

    if lsize_thread4:
        time.sleep(5)
        set_lot_label4()
    else:
        return
         
def place_realorder():
    """
    Function to Place orders based on the values specified on
    orderscreen. Order is managed by creating `ManageOrder` object
    which updates profit, current sop and other values. It also inserts
    the order in `OrderData//orders_data.xlsx` after it is placed.
    """
    global last_num,trade_threads,y_value, price_thread1, price_thread2,\
    price_thread3, price_thread4, lsize_thread1, lsize_thread2, lsize_thread3, lsize_thread4, EXIT_ALL,\
    isop_thread

    
    EXIT_ALL = 0
    product_value = product_type.get()
    quant = [l1.get(),l2.get(),l3.get(),l4.get()]
    data = None
    count = 4 - quant.count(0)
    date_today = str(datetime.now())
    i1 = s1instru.get()
    i2 = s2instru.get()
    i3 = s3instru.get()
    i4 = s4instru.get()
    b1 = bs1.get()
    b2 = bs2.get()
    b3 = bs3.get()
    b4 = bs4.get()
    bs = [b1,b2,b3,b4]
    
    ex1 ,ex2 ,ex3 ,ex4 = exp1.get(),exp2.get(),exp3.get(), exp4.get()
    pc1, pc2, pc3, pc4 = otype1.get(), otype2.get(), otype3.get(), otype4.get()
    pc = [pc1,pc2,pc3,pc4]
    strike_price = [price1.get(),price2.get(),price3.get(),price4.get()]
    expiry_dates = [ex1,ex2,ex3,ex4]

    # buy_sell = [b1,b2,b3,b4]
    instru = [i1,i2,i3,i4]
    bs, pc, expiry_dates, instru, quant, strike_price = zip(*sorted(zip(bs, pc, expiry_dates, instru, quant,strike_price),key=lambda x: x[0]))
    instru = list(instru)
    expiry_dates = list(expiry_dates)
    for r in range(len(instru)):
        if instru[r]=="":
            instru[r] = "None"
            expiry_dates[r] = "None"
        
    isop = 0 #initial sop before placing order.
    # data variable store values related to the order.
    try:
        api_type = PlaceOrderClass.cls.__name__
    except AttributeError as e:
        api_type = "KiteFree"
        logging.error(e,exc_info=True)

    last_num+=1
    data = [last_num,date_today,*instru,*bs,*pc,sdelta.get(),tdelta.get(),*strike_price,*expiry_dates,*quant,product_value, api_type, count]
    
    m = MarketApi()
    if data !=None:
        
        for j in range(len(bs)):
            if bs[j]=="None":
                continue
          
            name = instru[j]

            exp_date = convert_date(expiry_dates[j])
            series = "OPTSTK"
            if "NIFTY" in name:
                series = "OPTIDX"
            o = "CE"
            if pc[j]=="PE":
                o = "PE"
                        
            try:
                _, id_ = get_instru_id(name,o,exp_date,strike_price[j],series)
                instru_lot_size = _
                m.get_quote(id_,2,1502)

            except Exception as e:
                messagebox.showerror("Error","Error while obtaining intrument id. Couldn't place order.")
                logging.error(e,exc_info=True)
                return

            if bs[j]==BUY:
                price = m.asks[0]
                isop+=(quant[j]*price)
                slide = BUY
            else:
                price = m.bids[0]
                isop-=(quant[j]*price)
                slide = SELL
            
            try:
                Place = PlaceOrderClass
                tsymbol = exchange_name(name, exp_date,strike_price[j],o) # Trading symbol
                
                def make_first_order(id_,slide,q,tradingsymbol,instru_lot_size,product_type):
                    Place.place_order(id_=id_,slide=slide,q=q,tradingsymbol=tradingsymbol,size=instru_lot_size,product_type=product_type)

                make_first_order(id_,slide,quant[j],tsymbol,instru_lot_size,product_type=product_value)
                

                messagebox.showinfo("ORDER STATUS",f"{tsymbol} is placed!")


            except Exception as e:
                print("Order not placed",e)
                messagebox.showerror("ERROR",f"{tsymbol}\n{e}")
                logging.error(e,exc_info=True)
                return
        
            # stop updating market price.
            price_thread1 = 0
            price_thread2 = 0
            price_thread3 = 0
            price_thread4 = 0

            lsize_thread1 = 0
            lsize_thread2 = 0
            lsize_thread3 = 0
            lsize_thread4 = 0

            isop_thread = 0
            
        data.append(isop)

        order = ManageOrder(data)
        order.create_widgets()
        order.current_sop()
        order.pending_order()
        order.update_widgets()
        # Redirect to Preorder Screen to place more orders.
        preorderscreen()
        # t = Thread(target=insert_data,args=(data,columns,'.//OrderData//order_data.xlsx'))
        # t.start()
        insert_data(data,columns,'.\\OrderData\\order_data.xlsx')

def stop_bg_threads():
    global price_thread1, price_thread2, price_thread3, price_thread4,\
        lsize_thread1, lsize_thread2, lsize_thread3, lsize_thread4, isop_thread

    price_thread1 = 0
    price_thread2 = 0
    price_thread3 = 0
    price_thread4 = 0

    lsize_thread1 = 0
    lsize_thread2 = 0
    lsize_thread3 = 0
    lsize_thread4 = 0

    isop_thread = 0

def get_class(string):

    if string.lower()=="kitefree":
        return AdapterApi(None)
    elif string.lower()=="marketapi":
        return AdapterApi(MarketApi)
    elif string.lower()=="kite":
        return AdapterApi(Kite)
    else:
        raise Exception("Invalid String")
    

def start_last_orders():
    """
    Start managing notcompleted orders.
    """
    mssg = messagebox.askyesno("Start Orders?","Do you want to start non completed orders?")
    if mssg:
        dataframe = fetch_data('.\\OrderData\\notcompleted.xlsx')
        for data in dataframe:
            order = ManageOrder(data)
            order.create_widgets()  
            order.current_sop()      
            order.update_widgets()
    
def get_instru_id(symbol_,option,expiry,price_,series_):
    """
    Returns instrument id and lot size of a trading symbol.

    Parameters
    ----------
    symbol_ : str
        trading symbol name
    option : str
        trading option (PE/CE)
    expirty : str
        expirty date
    price_ : str
        strike price
    series_ : str
        series to which symbol belongs (OPTIDX/OPTSTK)

    Returns
    -------
    lot : int
        lot size of symbol_
    id_ : int
        instrument id of symbol_
    """
    m = MarketApi()
    lot , id_ = m.get_option_symbol(symbol=symbol_,otype=option,expirydate=expiry,sprice=price_,series=series_)
    return lot,id_


class ManageOrder:
    """
    Class to managge order.

    Methods
    -------
    display_symbol()
        display trading symbols on Trademanagement Screen.
    current_sop():
        calculate current sop.
    profit_loss()
        calculate profit/loss.
    exit_trade()
        exit trade.
    destroy()
        disable widgets for order.
    create_widgets()
        create widgets to display order details.
    update_widegts()
        update order details.
    square_off()
        Square off an order.
    pending_order()
        handle non executed orders.
    delete_data_object()
        delete order from notcompleted.xlsx

    """
    def __init__(self,data) :
        
        self.data = data
        print(data)
        print(data[-3])
        self.y  = 20
        self.sn = data[0]
        self.product = data[-4]
        self.frame = Frame(display_frame,bg='#c7c8c9')
        self.frame.pack(fill='x',expand=1,ipady=80,side=TOP,pady=5)
        self.quantity = data[24:28]
        self.date = data[1]
        self.instrument = data[2:6]
        self.bs = data[6:10]
        self.pc = data[10:14]
        self.initsop = data[-1]
        self.sld = data[14]
        self.targetd  = data[15]
        self.strike_price = data[16:20]
        self.sl = (self.initsop-self.sld) #variable to store stop loss value
        self.target = (self.initsop + self.targetd) #variable to store traget
        self.pl = 0 # profit and loss value
        self.expiry_data = data[20:24]
        self.csop = self.initsop #current sop
        self.market  = get_class(data[-3])
        self.num = data[0]
        self.quit = 0
        self.count = data[-2]
        self.sl_variable = StringVar()
        self.target_variable = StringVar()
        self.sldelta_var  = StringVar()
        self.tdelta_var = StringVar()
        self.sldelta_var.set(str(self.sld))
        self.tdelta_var.set(str(self.targetd))
        self.MINISEC = CALL_FEQ


    def display_symbol(self):
        """
        Display Trading symbols of instrument in an
        order. It helps to recogonize the order. Trading symbol
        follows zerodha conventions for naming trading symbol.
        """
        x_place_value = 0.02
        for i in range(len(self.instrument)):

            if self.instrument[i] and self.expiry_data[i] not in ['',None,'None']:
                name = self.instrument[i]

                o = "PE"
                if self.pc[i]=="CE":
                    o = "CE"

                tsymbol = exchange_name(name, convert_date(self.expiry_data[i]),self.strike_price[i],o)
                Label(self.frame,text=tsymbol,bg='#c7c8c9').place(y=130,relx=x_place_value)
                x_place_value+=0.22
        

    def current_sop(self):
        """
        Calculates current SOP for an order and update the profit/loss
        value accordingly.
        """
        sop = 0
        for i in range(len(self.instrument)):
            if self.instrument[i] and self.expiry_data[i] not in ['',None,'None']:
                
                
                name = self.instrument[i]
                
                series = "OPTSTK"
                if name.find("NIFTY")!=-1:
                    series = "OPTIDX"

                if self.pc[i]=="PE":
                    o = "PE"

                elif self.pc[i]:
                    o = "CE"
                try:

                    _, id_ = get_instru_id(name,o,convert_date(self.expiry_data[i]),self.strike_price[i],series)
                    m = MarketApi()
                    m.get_quote(id_,2,1502)
                    # print(m.asks[0])
                    # print(m.bids[0])
                    if self.bs[i]==SELL: # check BUY/SELL value
                        price = m.asks[0]
                        sop-=(self.quantity[i]*price)
                    else:
                        price = m.bids[0]  
                        sop+=(self.quantity[i]*price)
                    # print(sop,self.quantity,price)
                except  Exception as e:
                    print(e)
                    logging.error(f"{e} INSTU {name} EXPIRY {self.expiry_data[i]} SP {self.strike_price[i]}",exc_info=True)

            else:
                continue
        
        self.csop = sop 
        self.currsop['text'] = f"{self.csop:.2f}" #update current sop
        print(self.currsop['text'])
        print("Sec : ",self.MINISEC)
        self.profit_loss() # to update profit/loss

    def profit_loss(self):
        """
        Updates profit value for an order based on current sop
        and inital sop.
        """
        self.pl = (self.csop - self.initsop)
        self.p_and_l['text'] = f"{self.pl:.2f}"

    def exit_trade(self):
        """
        Exit trade/order by squaring it off. User is prompted
        to a confirmation widget before exiting trade.
        """
        mssg = messagebox.askyesno("Exit Trade","DO you want to exit Trade ?")
        if mssg:
            self.square_off()
            self.delete_data_object(self.sn, self.date)
            self.destroy()

    def destroy(self):
        """
        Disables all the widget associated with an order
        once order is completed/squared off.
        """
        self.quit = 1
        self.isop['state'] = 'disable'
        self.currsop['state'] = 'disable'
        self.sdelta['state'] = 'disable'
        self.p_and_l['state'] = 'disable'
        self.tdelta['state'] = 'disable'
        self.exit_trade['state'] = 'disable'
        self.exit_trade['bg'] = 'red'
        self.update_button['state'] = 'disable'
        
    def create_widgets(self):
        """
        Creates Widgets which display details of an order
        like initial sop, current sop, profit/loss, etc.
        """
        self.isop = Label(self.frame,text=f"{self.initsop:.2f}")
        self.isop.place(x=30,y=self.y,width=80)

        self.currsop = Label(self.frame,text=f"{self.csop:.2f}")
        self.currsop.place(x=150,y=self.y,width=80)
        
        self.sdelta = Label(self.frame,textvariable= self.sl_variable)
        self.sdelta.place(x=390,y=self.y,width=82)
        self.sl_variable.set(f"{self.sl:.2f}")

        self.p_and_l  = Label(self.frame,text=f"{self.pl:.2f}")
        self.p_and_l.place(x=510,y=self.y,width=82)

        self.tdelta = Label(self.frame,textvariable=self.target_variable)
        self.tdelta.place(x=280,y=self.y,width=80)
        self.target_variable.set(f"{self.target:.2f}")

        self.exit_trade  = Button(self.frame,text='Exit',command=self.exit_trade)
        self.exit_trade.place(x=630,y=self.y)
        
        Label(self.frame, text='SL delta :').place(x=30,y=self.y+50)
        self.sldelta_input = Entry(self.frame,textvariable=self.sldelta_var)
        self.sldelta_input.place(x=90,y=self.y+50,width=90)
        
        Label(self.frame,text='Target delta :').place(x=250,y=self.y+50)
        self.tdelta_input = Entry(self.frame,textvariable=self.tdelta_var)
        self.tdelta_input.place(x=330,y=self.y+50,width=90)

        self.update_button = Button(self.frame,text='Update Delta',command=self.update_delta)
        self.update_button.place(x=450,y=self.y+50)

        self.display_symbol()


    def update_widgets(self,*args):
        """
        Updates the details of an order like current sop
        and profit/loss. It also check if order profit is
        with in specified range (stop loss and target) for 
        squaring off.

        Orders are squared off automatically after 15:00 and are 
        added to notcompleted.xlsx.
        """
        if self.quit!=1 : 

            self.current_sop()
            time = datetime.now().time()
            if time.hour>=15 and time.minute>=20:
                self.destroy()
                self.delete_data_object(self.sn,self.date)
                return
                
                
            try:
               
                if ((self.csop)>=float(self.target_variable.get())) or ((self.csop) < float(self.sl_variable.get())) and (self.sld!=0 and self.targetd!=0):
                    self.square_off()
                    self.delete_data_object(self.sn,self.date)
                    self.destroy()
                    return 

                elif (((self.csop)<float(self.target_variable.get()) and abs(float(self.csop)-float(self.target_variable.get()))<=TARGETDIFF) or ((self.csop)>float(self.sl_variable.get()) and abs(float(self.csop)-float(self.sl_variable.get()))<=SLDIFF)) and (self.sld!=0 and self.targetd!=0):
                    self.MINISEC = NEW_CALL_FEQ
                    
                elif EXIT_ALL:
                    self.square_off()
                    self.delete_data_object(self.sn,self.date)
                    self.destroy()
                    return
                    
                else:
                    self.MINISEC = CALL_FEQ
                    
            except Exception as e:
                logging.error(e,exc_info=True)

            root.after(self.MINISEC,self.update_widgets,self)
        else:
            print("DATA SAVED!")

    def square_off(self):
        """
        Squares off an order. BUY order is changed to SELL order and 
        vise versa.
        """
        for i in range(len(self.instrument)):
            if self.instrument[i] and self.expiry_data[i] not in ['',None,'None']:
                name = self.instrument[i]
                series = "OPTSTK"
                if name.find("NIFTY")!=-1:
                   series = "OPTIDX"

                o = "PE"
                if self.pc[i]=="CE":
                    o = "CE"
                        
                slide = "BUY"
                if self.bs[i]=="BUY":
                    slide = "SELL"
                        
                _, id_ = get_instru_id(name,o,convert_date((self.expiry_data[i])),self.strike_price[i],series)
                lot = _
                #Trading symbol (zerodha)
                tsymbol = exchange_name(name, convert_date(self.expiry_data[i]),self.strike_price[i],o)
                #Place order
                self.place_order(id_,slide,self.quantity[i],tsymbol,lot)

    
    def pending_order(self):
        """
        Stores details of order which is not completed. Details are stored in 
        notcompleted.xlsx. 
        """
        new_data = [self.num,self.data[1],*self.instrument,*self.bs,*self.pc,self.sld,self.targetd,*self.strike_price,*self.expiry_data,*self.quantity,self.product,self.data[-3],self.data[-2],self.initsop]
        t = Thread(target=insert_data,args=(new_data,columns,'.\\OrderData\\notcompleted.xlsx'))
        t.start()

    def place_order(self,id_,slide,q,tsymbol,size):
        """
        Place order inorder to square off.
        """
        # t = Thread(target=self.market.place_order,args=(id_,slide,q,tsymbol,enctoken))
        # t.start()
        def make_order(id_,slide,q,tradingsymbol,instru_lot_size,product_type):
            nonlocal self
            self.market.place_order(id_=id_,slide=slide,q=q,tradingsymbol=tradingsymbol,size=instru_lot_size,product_type=product_type)
        
        try:
            make_order(id_,slide,q,tsymbol,size,self.product)
            print("order placed")
        except Exception as e:
            print("ERROR occured while placing square off order.",e)
            logging.error(e,exc_info=True)

    def delete_data_object(self, sn, date):
        """
        Deleted order from notcompleted.xlsx if it is 
        completed.
        """
        global last_cnum
        # pending_df = 
        curdate = str(datetime.now())
        pending_df = pd.read_excel('.\\OrderData\\notcompleted.xlsx')
        data = pending_df.loc[(pending_df[columns[0]]==sn) & (pending_df[columns[1]]==date)]
        if data.values.tolist:
            
            row_count = data.index[0] + 2
            
            delete_thread = Thread(target=delete_data,args=(row_count,))
            delete_thread.start()
            
            row = data.values.tolist()[0]
            row[0] = last_cnum
            row+=[curdate,self.csop]
            last_cnum+=1

            insert_data(row,completed_df.columns,filename='.\\OrderData\\completed.xlsx')

    def update_delta(self):
        self.sld = float(self.sldelta_var.get())
        self.targetd = float(self.tdelta_var.get())
        self.target = (self.initsop + self.targetd)
        self.sl = (self.initsop-self.sld)
        self.target_variable.set(f"{self.target:.2f}")
        self.sl_variable.set(f"{self.sl:.2f}")
        self.update_noncompleted_order()
        
    def update_noncompleted_order(self):
        pending_df = pd.read_excel('.\\OrderData\\notcompleted.xlsx')
        data = pending_df.loc[(pending_df[columns[0]]==self.sn) & (pending_df[columns[1]]==self.date)]
        t = Thread(target=change_data,args=(data, self.sld, self.targetd))
        t.start()
        

def dummy_buy_ask():
    t = Thread(target=buy_ask_get)
    t.start()

def buy_ask_get():
    """
    Gets the buy/ask value for a instrument on PreOrder Screen.
    StikePrice is the 1st strike price given on Preorder Screen.
    """
    try:
        if not (cp.get() and instrument.get() and expiry.get() and st1.get()):
            messagebox.showerror("Error","Missing Some values")
            return 0

        if cp.get()==2:
            o = 'PE'
        else:
            o = 'CE'

        series='OPTSTK'
        if 'NIFTY' in instrument.get():
            series='OPTIDX'
    except Exception as e:
        logging.error(e,exc_info=True)
    try :

        _, id_ = get_instru_id(instrument.get(),o,convert_date(expiry.get()),st1.get(),series)
        m  = MarketApi()
        m_bid, m_ask = m.get_quote(id_,2,1502)

        Bid_label['text'] = f"{m_bid[0]:.2f}"
        Ask_label['text'] = f"{m_ask[0]:.2f}"

    except Exception as e:
        print(e)
        messagebox.showerror("Error","Oops, something went wrong.\nTry again.")
        logging.error(e,exc_info=True)
        return 0
        
    
def sys_login():
    """
    Login Fucntion for IFL API.
    """
    def login():
        try:
            mp = MarketApi()
            mp.login()
            mp.logini()

        except Exception as e:
            messagebox.showerror("Login Error",str(e))
            logging.error(e,exc_info=True)
        else:
            messagebox.showinfo("Login Successful","Login for IFL API successful!")
        
    t = Thread(target=login,args=())
    t.start()

def kite_free_login():
    """
    Login Function for KiteFree.
    """
    def login():

        try:
            adpt = AdapterApi(None)
            adpt.login_kitefree()
        except Exception as e:
            messagebox.showerror("Error in Login",e)
            logging.error(e,exc_info=True)
        else:
            messagebox.showinfo("Login Successful","Loged in to KiteFree API.")

    t = Thread(target=login,args=())
    t.start()

def pending_order_start():
    try :

        start_orders = Thread(target=start_last_orders)
        start_orders.start()

    except xlrd.biffh.XLRDErroras as x:
        messagebox.showerror("Error","Nothing in file.")
        logging.error(x,exc_info=True)
    except Exception as e:
        messagebox.showerror("Error",e)
        logging.error(e,exc_info=True)

###-main_###

root = Tk()
root.geometry("950x600")
root.title("AlgoApp")




menu = Menu(root)
submenu1 = Menu(menu,tearoff=0,activebackground='white',activeforeground="black")
submenu1.add_command(label="PreorderScreen",command=preorderscreen,)
submenu1.add_command(label="OrderScreen",command=ordermenuscreen)
submenu1.add_command(label="ManageTrade",command=tradescreen)
submenu2 = Menu(menu,tearoff=0,activebackground='white',activeforeground="black")

submenu2.add_command(label="IFL Login",command=sys_login)
submenu2.add_command(label="Kite Free",command=kite_free_login)
submenu2.add_command(label="Kite API")

menu.add_cascade(menu=submenu1,label="Options")
menu.add_cascade(menu=submenu2,label="Login")
menu.add_command(label=" API ",command=order_api)
menu.add_command(label="Start Old Orders", command=pending_order_start)
menu.add_command(label="Exit all",command=exit_all_trade)


root.config(menu=menu)
### variables Preorder
ls = IntVar()
ls.set(-1)
cp = IntVar()
cp.set(-1)
st1 = IntVar()
st2 = IntVar()
st3 = IntVar()
st4 = IntVar()
lots = IntVar()
lots.set(1)
instu = StringVar()
expiry = StringVar()


### Variables Order
total_active = 4
bs1 = StringVar()
bs2 = StringVar()
bs3 = StringVar()
bs4 = StringVar()

instru1 = StringVar()
instru2 = StringVar()
instru3 = StringVar()
instru4 = StringVar()

otype1 = StringVar()
otype2 = StringVar()
otype3 = StringVar()
otype4 = StringVar()

expiry1  = StringVar()
expiry2  = StringVar()
expiry3  = StringVar()
expiry4  = StringVar()

price1 = IntVar()
price2 = IntVar()
price3 = IntVar()
price4 = IntVar()

l1 = IntVar()
l2 = IntVar()
l3 = IntVar()
l4 = IntVar()

lotdata1 = StringVar()
lotdata2  = StringVar()
lotdata3  = StringVar()
lotdata4  = StringVar()

premium1 = DoubleVar()
premium2 = DoubleVar()
premium3 = DoubleVar()
premium4 = DoubleVar()

sdelta = IntVar()
tdelta = IntVar()

product_type = StringVar()
product_type.set("MIS")

date_list = getexpiry()

## Frames

mainframe = Frame(root,bg="white")
mainframe.place(relwidth=1,relheight=1)

preorderframe = Frame(root,bg='white')
preorderframe.place(relwidth=1,relheight=1)

orderframe = Frame(root,bg='white')
orderframe.place(relwidth=1,relheight=1)

mainframe.tkraise()
mainframe.tkraise()

### main frame

start = Button(mainframe,text="Start",command=preorderscreen)
start.place(relx=0.48,rely=0.65,width=90,height=40)
### Preorder Frame

long = Radiobutton(preorderframe,variable=ls,value=1,text="Long",bg='white')
long.place(x=100,y=80)

short = Radiobutton(preorderframe,variable=ls,value=0,text="Short",bg='white')
short.place(x=100,y=120)

ces = Radiobutton(preorderframe,variable=cp,value=1,text="CE SPREAD",command=dummy_radio_fun,bg='white')
pes = Radiobutton(preorderframe,variable=cp,value=2,text="PE SPREAD",command=dummy_radio_fun,bg='white')
cers = Radiobutton(preorderframe,variable=cp,value=3,text="CE RATIO SPREAD",command=dummy_radio_fun,bg='white')
cef = Radiobutton(preorderframe,variable=cp,value=4,text="CE FLY",command=dummy_radio_fun,bg='white')
condor = Radiobutton(preorderframe,variable=cp,value=5,text="CONDOR",command=dummy_radio_fun,bg='white')

ces.place(x=320,y=80)
pes.place(x=320,y=120)
cers.place(x=480,y=80)
cef.place(x=480,y=120)
condor.place(x=690,y=80)

Label(preorderframe,text='Strike Price',bg='white').place(x=100,y=200)
s1 = Entry(preorderframe,textvariable=st1)
s1.place(x=100,y=280,height=30)

s2 = Entry(preorderframe,textvariable=st2)
s2.place(x=100,y=340,height=30)

s3 = Entry(preorderframe,textvariable=st3)
s3.place(x=100,y=400,height=30)

s4 = Entry(preorderframe,textvariable=st4)
s4.place(x=100,y=460,height=30)


options = ["NIFTY","BANKNIFTY"]

Label(preorderframe,text='Instrument',bg='white').place(x=340,y=200)
instrument = AutocompleteCombobox(preorderframe,textvariable=instu,values=options)
instrument.set_completion_list(options)
instrument.place(x=320,y=278)

Label(preorderframe,text='Bid :',bg='white').place(x=330,y=360)
Bid_label = Label(preorderframe,text='None',fg='blue',bg='white')
Bid_label.place(x=370,y=360)

Label(preorderframe,text='Ask :',bg='white').place(x=440,y=360)
Ask_label = Label(preorderframe,text='None',bg='white',fg='red')
Ask_label.place(x=480,y=360)

Label(preorderframe,text='Expiry',bg='white').place(x=570,y=200)
edate = AutocompleteCombobox(preorderframe,textvariable=expiry,)
edate.place(x=550,y=278)
edate['values'] = date_list


Label(preorderframe,text='No. Lot',bg='white').place(x=770,y=200)
lot = Entry(preorderframe,textvariable=lots)
lot.place(x=750,y=278,width=50)

set_order = Button(preorderframe,text="Set Order",command=start_setorder)
set_order.place(x=400,y=540)

clear_button = Button(preorderframe,text='Clear',command=clear)
clear_button.place(x=500,y=540)

buy_ask = Button(preorderframe,text='Get Price',command=dummy_buy_ask)
buy_ask.place(x=600,y=540)


### OrderFrame
Label(orderframe,text='Order Type',bg='white').place(x=30,y=30)
s1b = Radiobutton(orderframe, variable=bs1,text='BUY',value="BUY",bg='white')
s1s = Radiobutton(orderframe, variable=bs1,text='SELL',value="SELL",bg='white')
s2b = Radiobutton(orderframe, variable=bs2,text='BUY',value="BUY",bg='white')
s2s = Radiobutton(orderframe, variable=bs2,text='SELL',value="SELL",bg='white')

s3b = Radiobutton(orderframe, variable=bs3,text='BUY',value="BUY",bg='white')
s3s = Radiobutton(orderframe, variable=bs3,text='SELL',value="SELL",bg='white')

s4b = Radiobutton(orderframe, variable=bs4,text='BUY',value="BUY",bg='white')
s4s = Radiobutton(orderframe, variable=bs4,text='SELL',value="SELL",bg='white')

list_b = [s4b,s3b,s2b,s1b]
list_s = [s4s,s3s,s2s,s1s]

s1b.place(x=40,y=80)
s1s.place(x=40,y=120)

s2b.place(x=40,y=180)
s2s.place(x=40,y=220)

s3b.place(x=40,y=280)
s3s.place(x=40,y=320)

s4b.place(x=40,y=380)
s4s.place(x=40,y=420)

inoption = ['NIFTY', 'BANKNIFTY']
Label(orderframe,text='Instrument',bg='white').place(x=135,y=30)
s1instru = AutocompleteCombobox(orderframe, textvariable=instru1, values=inoption)
s2instru = AutocompleteCombobox(orderframe, textvariable=instru2, values=inoption)
s3instru = AutocompleteCombobox(orderframe, textvariable=instru3, values=inoption)
s4instru = AutocompleteCombobox(orderframe, textvariable=instru4, values=inoption)

s1instru.set_completion_list(inoption)
s2instru.set_completion_list(inoption)
s3instru.set_completion_list(inoption)
s4instru.set_completion_list(inoption)

s1instru.bind('<<ComboboxSelected>>',)
list_instru = [s4instru,s3instru,s2instru,s1instru]

s1instru.place(x=120,y = 90)
s2instru.place(x=120,y = 190)
s3instru.place(x=120,y = 290)
s4instru.place(x=120,y = 390)

Label(orderframe,text="Option Type",bg='white')
s1p = Radiobutton(orderframe, variable=otype1,text="PUT",value="PE",bg='white')
s1c = Radiobutton(orderframe, variable=otype1,text="CALL",value="CE",bg='white')

s2p = Radiobutton(orderframe, variable=otype2,text="PUT",value="PE",bg='white')
s2c = Radiobutton(orderframe, variable=otype2,text="CALL",value="CE",bg='white')

s3p = Radiobutton(orderframe, variable=otype3,text="PUT",value="PE",bg='white')
s3c = Radiobutton(orderframe, variable=otype3,text="CALL",value="CE",bg='white')

s4p = Radiobutton(orderframe, variable=otype4,text="PUT",value="PE",bg='white')
s4c = Radiobutton(orderframe, variable=otype4,text="CALL",value="CE",bg='white')

s1p.place(x=280,y=80)
s1c.place(x=280,y=120)

s2p.place(x=280,y=180)
s2c.place(x=280,y=220)

s3p.place(x=280,y=280)
s3c.place(x=280,y=320)

s4p.place(x=280,y=380)
s4c.place(x=280,y=420)

list_sp = [s4p,s3p,s2p,s1p]
list_sc = [s4c,s3c,s2c,s1c]
Label(orderframe,text="Expiry Date",bg='white').place(x=350,y=30)
exp1 = AutocompleteCombobox(orderframe,textvariable=expiry1)
exp2 = AutocompleteCombobox(orderframe,textvariable=expiry2)
exp3 = AutocompleteCombobox(orderframe,textvariable=expiry3)
exp4 = AutocompleteCombobox(orderframe,textvariable=expiry4)

exp1.place(x=360,y=90)
exp2.place(x=360,y=190)
exp3.place(x=360,y=290)
exp4.place(x=360,y=390)

exp1['values']=date_list
exp2['values']=date_list
exp3['values']=date_list
exp4['values']=date_list

list_exp = [exp4,exp3,exp2,exp1]
Label(orderframe,text='Strike Price',bg='white').place(x=560,y=30)
sprice1 = Entry(orderframe, textvariable=price1)
sprice2 = Entry(orderframe, textvariable=price2)
sprice3 = Entry(orderframe, textvariable=price3)
sprice4 = Entry(orderframe, textvariable=price4)

sprice1.place(x=550,y=90,width=70)
sprice2.place(x=550,y=190,width=70)
sprice3.place(x=550,y=290,width=70)
sprice4.place(x=550,y=390,width=70)
# 
list_sprice = [sprice4,sprice3,sprice2,sprice1]
Label(orderframe,text='No. of Lots',bg='white').place(x=660,y=30)
lot1 = Entry(orderframe,textvariable=l1)
lot2 = Entry(orderframe,textvariable=l2)
lot3 = Entry(orderframe,textvariable=l3)
lot4 = Entry(orderframe,textvariable=l4)

lot1.place(x=650,y=90,width=50)
lot2.place(x=650,y=190,width=50)
lot3.place(x=650,y=290,width=50)
lot4.place(x=650,y=390,width=50)
# 
list_lot = [lot4,lot3,lot2,lot1]
Label(orderframe,text='Lot Size',bg='white').place(x=750,y=30)
lotlabel1 = Label(orderframe,text='',textvariable=lotdata1)
lotlabel2 = Label(orderframe,text='',textvariable=lotdata2)
lotlabel3 = Label(orderframe,text='',textvariable=lotdata3)
lotlabel4 = Label(orderframe,text='',textvariable=lotdata4)

lotlabel1.place(x=740,y=90,width=80)
lotlabel2.place(x=740,y=190,width=80)
lotlabel3.place(x=740,y=290,width=80)
lotlabel4.place(x=740,y=390,width=80)
# 
list_lotlabel = [lotlabel4,lotlabel3,lotlabel2,lotlabel1]
Label(orderframe,text='Price',bg='white').place(x=860,y=30)
mkprice1 = Label(orderframe,text='',textvariable=premium1)
mkprice2 = Label(orderframe,text='',textvariable=premium2)
mkprice3 = Label(orderframe,text='',textvariable=premium3)
mkprice4 = Label(orderframe,text='',textvariable=premium4)

mkprice1.place(x=850,y=90,width=80)
mkprice2.place(x=850,y=190,width=80)
mkprice3.place(x=850,y=290,width=80)
mkprice4.place(x=850,y=390,width=80)
# 
list_mkprice = [mkprice4,mkprice3,mkprice2,mkprice1]

place_button = Button(orderframe,text='Place Order',bg='#0a9cf0',command=dummy_place_order)
place_button.place(x=100,y=500,width=70,height=40)

sldelta = Entry(orderframe,textvariable=sdelta)
targetdelta = Entry(orderframe,textvariable=tdelta)
Label(orderframe,text='SL Delta : ',bg='white').place(x=370,y=500)
sldelta.place(x=450,y=500,height=30,width=60)

Label(orderframe,text="Target Delta : ",bg='white').place(x=540,y=500)
targetdelta.place(x=670,y=500,height=30,width=60)

Label(orderframe,bg='#0a9cf0').place(relwidth=1,height=5,x=0,y=60)
Label(orderframe,bg='#707070').place(relwidth=1,height=3,x=0,y=155)
Label(orderframe,bg='#707070').place(relwidth=1,height=3,x=0,y=255)
Label(orderframe,bg='#707070').place(relwidth=1,height=3,x=0,y=355)

mis = Radiobutton(orderframe,text="MIS",bg='white',value="MIS",variable=product_type)
mis.place(x=780,y=490)
normal = Radiobutton(orderframe,text="NRML",bg='white',value="NRML",variable=product_type)
normal.place(x=780,y=520)

isop_label = Label(orderframe,text='ISOP : ',bg='white')
isop_label.place(x=370,y=550)

isop_value = Label(orderframe, text="",bg='white')
isop_value.place(x=470,y=550,width=70)
## Trade Management

set_top() #create trademanagement screen
create_api_top() # create API selection screen.

root.mainloop()