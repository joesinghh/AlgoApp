import threading
from tkinter import *
from threading import Thread
from tkinter.ttk import Combobox
from ifl_api import MarketApi
from tkinter import messagebox
import pandas as pd
from datetime import date,datetime
from demo import delete_data, fetch_data, insert_data, insert_data_main, fetch_data
from Auto import AutocompleteCombobox
import platform
import time
import xlrd
from Adapter import AdapterApi
from exchange import exchange_name

date_today = str(date.today())

dataframe = pd.read_excel("order_data.xlsx")
pending_df = pd.read_excel('pending.xlsx')

try :
    last_num = dataframe['SN'].iloc[-1]
except IndexError:
    last_num = 1
columns = dataframe.columns
# print(columns)

trade_threads  = 0
y_value = 100

mp = MarketApi()

mp1 = MarketApi()
mp2 = MarketApi()
mp3 = MarketApi()
mp4 = MarketApi()

price_thread1 = 0
price_thread2 = 0
price_thread3 = 0
price_thread4 = 0

lsize_thread1 = 0
lsize_thread2 = 0
lsize_thread3 = 0
lsize_thread4 = 0

PlaceOrderClass = AdapterApi(None)

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


def preorderscreen():
    preorderframe.tkraise()

def orderscreen():
    print("hello")
    orderframe.tkraise()

def ordermenuscreen():
    print("hello 1")

    global price_thread1, price_thread2, price_thread3, price_thread4, lsize_thread1, lsize_thread2, lsize_thread3, lsize_thread4
    lsize_thread1, lsize_thread2, lsize_thread3, lsize_thread4 = 1, 1, 1, 1
    price_thread1, price_thread2, price_thread3, price_thread4 = 1, 1, 1, 1
    update_price_label()
    update_lotlabel()
    orderframe.tkraise()


def tradescreen():
    top.deiconify()


def getexpiry():

    symbol = "NIFTY"

    s = "OPTSTK"
    if "NIFTY" in symbol:
        s = "OPTIDX"

    dates = mp.get_expiry(symbol=symbol,esegment=2,series=s)
    date = []

    for  i in dates:
        d = datetime.strptime(i,"%Y-%m-%d").date()
        date.append(str(d.strftime("%d%b%Y")))
    
    return date


def inable_all():
    strike = [s1,s2,s3,s4]
    for i in strike:
        i['state'] = 'normal'

def disable_n(n):
    strike = [s4,s3,s2,s1]

    for i in range(1,n+1):
        strike[i-1]['state'] = 'disable'


def dummy_radio_fun():
    t = Thread(target=radio_fun)
    t.start()

def radio_fun():
    value = cp.get()
    if value!=-1:
        inable_all()
        if cp.get() in [1,2,3]:
            disable_n(2)
        elif cp.get() ==4:
            disable_n(1)

def setorder():
    if cp.get()==-1 or  ls==-1:
        messagebox.showerror("ERROR","Select a Valid Strategy")
        return 0

    try:
        if lots.get() <=0 :
            messagebox.showerror("ERROR","Invalid Lot Size")
    except Exception as e:
        messagebox.showerror("ERROR",e+" for Lot No.")
        return 0
        
    else:
        print(cp.get(),ls.get())

        update_order(cp.get())
        orderscreen()



def start_setorder():
    t = Thread(target=setorder)
    t.start()

def update_order(n):
    global price_thread1, price_thread2, price_thread3, price_thread4, lsize_thread1, lsize_thread2, lsize_thread3, lsize_thread4
    instru_value  = instu.get()
    expiry_date = expiry.get()
    lots_num = lots.get()
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
            bs1.set(1)
            bs2.set(0)

        else:
            bs1.set(0)
            bs2.set(1)

        otype1.set(1)
        otype2.set(1)


        num1, _ = get_instru_id(instru_value,"CE",expiry_date,st1.get(),s)
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
            bs1.set(1)
            bs2.set(0)
            bs3.set(1)

        else:
            bs1.set(0)
            bs2.set(1)
            bs3.set(0)

        otype1.set(1)
        otype2.set(1)
        otype3.set(1)

        num1, _ = get_instru_id(instru_value,"CE",expiry_date,st1.get(),s)
        num2 = num1
        num3 = num1
        
        lotdata1.set(str(num1))
        lotdata2.set(str(num2))
        lotdata3.set(str(num3))
        
        price1.set(st1.get())
        price2.set(st2.get())
        price3.set(st3.get())

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

        if ls.get()==1:
            bs1.set(1)
            bs2.set(0)
            bs3.set(1)
            bs4.set(0)
            otype1.set(1)
            otype2.set(1)
            otype3.set(0)
            otype4.set(0)

        else:
            bs1.set(0)
            bs2.set(1)
            bs3.set(0)
            bs4.set(1)
            otype1.set(0)
            otype2.set(0)
            otype3.set(1)
            otype4.set(1)

        num1, _ = get_instru_id(instru_value,"PE",expiry_date,st1.get(),s)
        num2, _ = get_instru_id(instru_value,"CE",expiry_date,st2.get(),s)
        num3 = num1
        num4 = num2
        # into thread
        
        lotdata1.set(str(num1))
        lotdata2.set(str(num2))
        lotdata3.set(str(num3))
        lotdata4.set(str(num4))


        price1.set(st1.get())
        price2.set(st2.get())
        price3.set(st3.get())
        price4.set(st4.get())

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


def clear():
    ls.set(-1)
    cp.set(-1)
    st1.set(0)
    st2.set(0)
    st3.set(0)
    st4.set(0)
    instrument.set("")
    edate['values'] = []
    edate.set("")
    lots.set(0)
    inable_all()


def set_top():
    global top, scroll_frame, display_frame

    top = Toplevel()
    scroll_frame = ScrollFrame(top)
    scroll_frame.pack(fill='both',expand=1)
    scroll_frame.tkraise()
    display_frame = Frame(scroll_frame.viewPort,bg='blue')
    display_frame.pack(side='left',anchor=NW,fill='both',expand=1)
    display_frame.tkraise()
    trade_frame = Frame(display_frame,bg='white')
    trade_frame.pack(fill='x',expand=1,ipady=100)
    trade_frame.tkraise()

    top.geometry('700x600')
    top.resizable(0,0)
    top.title("AlgoApp | Trade Management")
    top.withdraw()

    top.protocol('WM_DELETE_WINDOW',top.withdraw)
    Label(display_frame,text='Initial SOP',font=('Calibri',13)).place(x=30,y=20)
    Label(trade_frame,text='Current SOP',font=('Calibri',13)).place(x=160,y=20)
    Label(trade_frame,text='Target',font=('Calibri',13)).place(x=290,y=20)
    Label(trade_frame,text='SL',font=('Calibri',13)).place(x=390,y=20)
    Label(trade_frame,text='P&L',font=('Calibri',13)).place(x=490,y=20)

def order_api():
    api_top.deiconify()

def create_api_top():
    global api_variable, api_top
    api_top = Toplevel()
    api_top.geometry('200x200')
    api_top.resizable(0,0)
    api_variable = IntVar()
    api_variable.set(3)
    
    ifl = Radiobutton(api_top,text="IFL",variable=api_variable,value=1)
    ifl.pack()

    kite_api = Radiobutton(api_top,text='Kite',variable=api_variable,value=2)
    kite_api.pack()

    kite_free = Radiobutton(api_top,text='Kite Free',variable=api_variable,value=3)
    kite_free.pack()

    api_top.withdraw()
    api_top.protocol('WM_DELETE_WINDOW',api_top.withdraw)


def exit_order():
    print("Order exited")

def dummy_place_order():
    t = Thread(target=place_realorder)
    t.start()

def get_price(name,bs):
    m = MarketApi()
    price = m.get_quote(name,esegment=2,xts=1504)
    
def update_price_label():
    price_thread_list = [price_thread1, price_thread2,price_thread3, price_thread4]
    print("Update price")
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

def price_update_thread1():
    
    if instru1.get():
         
        o = 'CE'
        instru = instru1.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            _, id_ = get_instru_id(instru,o,expiry1.get(),price1.get(),series)
            m  = MarketApi()
            m_bid, m_ask = m.get_quote(id_,2,1502)
            if bs1.get()==1:
                premium1.set(str(m_ask[0]))
            else:
                premium1.set(str(m_bid[0]))

        except Exception as e:
            print(e,"For price1")
            pass

    if price_thread1:
        time.sleep(5)
        price_update_thread1()
    else:
        return

def price_update_thread2():
    
    if instru2.get():

        o = 'CE'
        instru = instru2.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            _, id_ = get_instru_id(instru,o,expiry2.get(),price2.get(),series)
            m  = MarketApi()
            m_bid, m_ask = m.get_quote(id_,2,1502)
            if bs2.get()==1:
                premium2.set(str(m_ask[0]))
            else:
                premium2.set(str(m_bid[0]))

        except Exception as e:
            print(e,"For price2")
            pass
    if price_thread2:
        time.sleep(5)
        price_update_thread2()
    else:
        return

def price_update_thread3():
    
    if instru3.get():

        o = 'CE'
        instru = instru3.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            _, id_ = get_instru_id(instru,o,expiry3.get(),price3.get(),series)
            m  = MarketApi()
            m_bid, m_ask = m.get_quote(id_,2,1502)
            if bs3.get()==1:
                premium3.set(str(m_ask[0]))
            else:
                premium3.set(str(m_bid[0]))

        except Exception as e:
            print(e,"For price3")
            pass
    if price_thread3:
        time.sleep(5)
        price_update_thread3()
    else:
        return

def price_update_thread4():
    if instru4.get():

        o = 'CE'
        instru = instru4.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            _, id_ = get_instru_id(instru,o,expiry4.get(),price4.get(),series)
            m  = MarketApi()
            m_bid, m_ask = m.get_quote(id_,2,1502)
            print(m_bid,m_ask)
            if bs4.get()==1:
                premium4.set(str(m_ask[0]))
            else:
                premium4.set(str(m_bid[0]))

        except Exception as e:
            print(e,"For price4")

    if  price_thread4:
        time.sleep(5)
        price_update_thread4()
    else:
        return
    
def update_lotlabel():
    lot_label_list = [lsize_thread1, lsize_thread2, lsize_thread3,lsize_thread4]
    print("Update lotsize")
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
    print("Thread Lot size")
    if instru1.get() and exp1['value']:
        o = 'CE'
        instru = instru1.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            lotsize, id_ = get_instru_id(instru,o,exp1['value'][1],price1.get(),series)
            lotdata1.set(str(lotsize))
        except Exception as e:
            print(e)
    if lsize_thread1:
        time.sleep(5)
        set_lot_label1()
    else:
        return

def set_lot_label2():
    print("Thread lot2")
    if instru2.get() and exp2['value']:
        o = 'CE'
        instru = instru2.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            lotsize, id_ = get_instru_id(instru,o,exp2['value'][1],price2.get(),series)
            lotdata2.set(str(lotsize))
        except Exception as e:
            print(e)
    if lsize_thread2:
        time.sleep(5)
        set_lot_label2()
    else:
        return

def set_lot_label3():
    print("Thread lot3")
    if instru3.get() and exp3['value']:
        o = 'CE'
        instru = instru3.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            lotsize, id_ = get_instru_id(instru,o,exp3['value'][1],price3.get(),series)
            lotdata3.set(str(lotsize))
        except Exception as e:
            print(e)
    if lsize_thread3:
        time.sleep(5)
        set_lot_label3()
    else:
        return

def set_lot_label4():
    print("Thread lot4")
    if instru4.get() and exp4['value']:
        o = 'CE'
        instru = instru4.get()
        series='OPTSTK'
        if 'NIFTY' in instru:
            series='OPTIDX'
    
        try :
            lotsize, id_ = get_instru_id(instru,o,exp4['value'][1],price4.get(),series)
            lotdata4.set(str(lotsize))
        except Exception as e:
            print(e)
    if lsize_thread4:
        time.sleep(5)
        set_lot_label4()
    else:
        return
         
def place_realorder():

    global last_num,trade_threads,y_value, price_thread1, price_thread2,\
    price_thread3, price_thread4

    buy_sell = [s1b,s2b,s3b,s4b]
    lots = [(l1,lotdata1),(l2,lotdata2),(l3,lotdata3),(l4,lotdata4)]
    quant = []
    data = None
    count = 0
    for i in range(len(buy_sell)):
        if buy_sell[i]['state']=='normal':
            quant.append(lots[i][0].get()*int(lots[i][1].get()))
            count+=1
        else:
            quant.append(None)
    
            
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

    buy_sell = [b1,b2,b3,b4]
    instru = [i1,i2,i3,i4]
    isop = 0
    if count==2:
        data = [last_num+1,date_today,i1,i2,None,None,b1,b2,None,None,otype1.get(),
        otype2.get(),None,None,sdelta.get(),tdelta.get(),price1.get(),price2.get(),None,None,ex1,ex2,None,None,*quant,count]
    elif count==3:
        data = [last_num+1,date_today,i1,i2,i3,None,b1,b2,b3,None,otype1.get(),
        otype2.get(),otype3.get(),None,sdelta.get(),tdelta.get(),price1.get(),price2.get(),price3.get(),None,ex1,ex2,ex3,None,*quant,count]
    
    elif count==4:
        data = [last_num+1,date_today,i1,i2,i3,i4,b1,b2,b3,b4,otype1.get(),
        otype2.get(),otype3.get(),otype4.get(),sdelta.get(),tdelta.get(),price1.get(),price2.get(),price3.get(),price4.get(),ex1,ex2,ex3,ex4,*quant,count]
    
    m = MarketApi()
    if data !=None:

        last_num+=1

        for j in range(0,count):
            
            name = instru[j]
            series = "OPTSTK"
            if "NIFTY" in name:
                series = "OPTIDX"
            o = "PE"
            if pc[j]:
                o = "CE"
            
            try:
                _, id_ = get_instru_id(name,o,expiry_dates[j],strike_price[j],series)
                instru_lot_size = _
                print(id_)
                m.get_quote(id_,2,1502)
            except:
                messagebox.showerror("An error occured.")
                return
            if bs[j]:
                price = m.bids[0]
                isop-=price
                slide = "BUY"
            else:
                price = m.asks[0]
                isop+=price
                slide = "SELL"

            
            try:
                Place = PlaceOrderClass
                tsymbol = exchange_name(name, expiry_dates[j],strike_price[j],o)

                enctoken = '3f8HTtmNKzdu1RH0O+KQFCNELlOC1wKD/e4X5VXyuD5GUOVnhvj8taL1M1Q2J1hbw07ICz2FYdJbtLoZuL3cpRh2q+vArbykdgpcXE9aAU0E6/xg7K9FEg=='


                def make_first_order(id_,slide,q,tradingsymbol,enctoken,instru_lot_size):
                    Place.place_order(id_=id_,slide=slide,q=q,tradingsymbol=tradingsymbol,enctoken=enctoken,size=instru_lot_size)
                    
                place_thread = Thread(target=make_first_order,args=(id_,slide,25,tsymbol,enctoken,instru_lot_size))
                place_thread.start()
            
                messagebox.showinfo("ORDER STATUS","Your order is placed!")
            except Exception as e:
                print(e)
                messagebox.showerror("ERROR","Oops something went wrong, Try again.")
                return

            price_thread1 = 0
            price_thread2 = 0
            price_thread3 = 0
            price_thread4 = 0
            

        data.append(isop)

        order = ManageOrder(data,y_value)
        order.create_widgets()
        order.current_sop()
        order.update_widgets()
        y_value+=80
        preorderframe.tkraise()
        # t = Thread(target=insert_data,args=(data,columns))
        # t.start()
        # insert_data(data,columns)

def start_last_orders():
    
    dataframe = fetch_data('pending.xlsx')
    for data in dataframe:
        order = ManageOrder(data)
        order.create_widgets()  
        order.current_sop()      
        order.update_widgets()
    

def get_instru_id(symbol_,option,expiry,price_,series_):
    m = MarketApi()
    lot , id_ = m.get_option_symbol(symbol=symbol_,otype=option,expirydate=expiry,sprice=price_,series=series_)
    return lot,id_

def start_tmanage(data,y_value):
    global trade_threads
    data_array = dataframe.values

    for i in data_array:
        m1 = ManageOrder(i,y_value,)
        m1.create_widgets()
        m1.update_widgets()


class ManageOrder:


    def __init__(self,data,dummy_value_y) :
        self.sn = None
        self.data = data
        self.y  = 50
        self.frame = Frame(display_frame,bg='blue')
        self.frame.pack(fill='x',expand=1,ipady=50)
        self.quantity = data[24:28]
        self.instrument = data[2:6]
        self.bs = data[6:10]
        self.pc = data[10:14]
        self.initsop = data[-1]
        self.sld = data[14]
        self.targetd  = data[15]
        self.strike_price = data[16:20]
        self.sl = self.initsop+self.sld
        self.target = self.initsop - self.targetd
        self.pl = 0
        self.expiry_data = data[20:24]
        self.csop = self.initsop
        self.market = PlaceOrderClass
        self.num = data[0]
        self.quit = 0
        # self.current_sop()
        self.sdelta_variable = StringVar()
        self.tdelta_variable = StringVar()


    def current_sop(self):
        sop = 0
        for i in range(len(self.instrument)):
            if self.instrument[i]!=None and self.instrument!='':
                print("instrument",self.instrument[i])
                name = self.instrument[i]
                series = "OPTSTK"
                if name.find("NIFTY")!=-1:
                    series = "OPTIDX"

                o = "PE"

                if self.pc[i]:
                    o = "CE"

                _, id_ = get_instru_id(name,o,self.expiry_data[i],self.strike_price[i],series)

                m = MarketApi()
                print(id_)
                m.get_quote(id_,2,1502)
            
                if not self.bs[i]:
                    
                    price = m.bids[0]
                    sop-=price
                else:
                    price = m.asks[0]  
                    sop+=price
                
                print(price,self.instrument[i])
            else:
                break
        
        print("Current SOP",sop)
        self.csop = sop
        self.currsop['text'] = f"{self.csop:.2f}"
        self.profit_loss()

    def profit_loss(self):
        self.pl = self.csop - self.initsop
        self.p_and_l['text'] = f"{self.pl:.2f}"

    def destroy(self):
        mssg = messagebox.askyesno("Exit Trade","DO you want to exit Trade ?")
        if mssg :
            self.quit = 1
            self.isop['state'] = 'disable'
            self.currsop['state'] = 'disable'
            self.sdelta['state'] = 'disable'
            self.p_and_l['state'] = 'disable'
            self.tdelta['state'] = 'disable'
            self.exit_trade['state'] = 'disable'
            self.exit_trade['bg'] = 'red'
        

    def create_widgets(self):
        self.isop = Label(self.frame,text=f"{self.initsop:.2f}")
        self.isop.place(x=40,y=self.y)

        self.currsop = Label(self.frame,text=f"{self.csop:.2f}")
        self.currsop.place(x=170,y=self.y)
        
        self.sdelta = Entry(self.frame,textvariable= self.sdelta_variable)
        self.sdelta.place(x=300,y=self.y)
        self.sdelta_variable.set(f"{self.sl:.2f}")

        self.p_and_l  = Label(self.frame,text=f"{self.pl:.2f}")
        self.p_and_l.place(x=500,y=self.y)

        self.tdelta = Entry(self.frame,textvariable=self.tdelta_variable)
        # self.tdelta.place(x=400,y=self.y)
        # self.tdelta_variable.set(f"{self.target:.2f}")

        self.exit_trade  = Button(self.frame,text='Exit',command=self.destroy)
        self.exit_trade.place(x=600,y=self.y)

    def update_widgets(self,*args):

        if self.quit!=1 and trade_threads!=1: 
            t = Thread(target=self.current_sop)
            t.start()
            print("update")
            time = datetime.now().time().strftime("%H:%M")
            if time=="15:00":
                self.pending_order()
                self.destroy()
                return

            if (self.pl>=eval(self.tdelta_variable.get())) or (self.pl < eval(self.sdelta_variable.get())):
                for i in range(len(self.instrument)):
                    if self.instrument[i]!=None and self.instrument!='':
                        name = self.instrument[i]
                        series = "OPTSTK"
                        if name.find("NIFTY")!=-1:
                            series = "OPTIDX"

                        o = "PE"
                        if self.pc[i]:
                            o = "CE"
                        
                        slide = "BUY"
                        if self.bs:
                            slide = "SELL"
                        
                        _, id_ = get_instru_id(name,o,self.expiry_data[i],self.strike_price[i],series)
                        lot = _
                        tsymbol = exchange_name(name, self.expiry_data[i],self.strike_price[i],o)
                        self.place_order(id_,slide,self.quantity[i],tsymbol,lot)

            root.after(60000,self.update_widgets,self)
        else:
            print("DATA SAVED!")
    
    def pending_order(self):
        new_data = [self.num,self.data[1],*self.instrument,*self.bs,*self.pc,self.sl,self.targetd,*self.strike_price,*self.expiry_data,*self.quantity,self.data[-2],self.csop]
        t = Thread(target=insert_data,args=(new_data,columns,'pending.xlsx'))
        t.start()

    def place_order(self,id_,slide,q,tsymbol,size):
        enctoken = '3f8HTtmNKzdu1RH0O+KQFCNELlOC1wKD/e4X5VXyuD5GUOVnhvj8taL1M1Q2J1hbw07ICz2FYdJbtLoZuL3cpRh2q+vArbykdgpcXE9aAU0E6/xg7K9FEg=='

        # t = Thread(target=self.market.place_order,args=(id_,slide,q,tsymbol,enctoken))
        # t.start()
        def make_order(id_,slide,q,tradingsymbol,enctoken,instru_lot_size):
            self.market.place_order(id_=id_,slide=slide,q=q,tradingsymbol=tradingsymbol,enctoken=enctoken,size=instru_lot_size)
        
        
        t = Thread(target=make_order,args=(id_,slide,q,tsymbol,enctoken,size))
        t.start()
        # t1 = Thread(target=delete_data,args=(self.data[0],self.data[1]))
        # t1.start()
        print("order placed")

    @staticmethod
    def delete_data(sn, date):
        data = pending_df[(pending_df[columns[0]==sn]) & (pending_df[columns[1]==date])]
        if data:
            row_count = 1
            complete_data = fetch_data('pending.xlsx')
            for d in complete_data:

                if d[0]==sn and d[1]==date:
                    break
                row_count+=1
            
            delete_thread = Thread(target=delete_data,args=(row_count,))
            delete_thread.start()



def dummy_buy_ask():
    t = Thread(target=buy_ask_get)
    t.start()

def buy_ask_get():

    if not (cp.get() and instrument.get() and expiry.get() and st1.get()):
        messagebox.showerror("Error","Missing Some values")
        return 0

    if cp.get():
        o = 'CE'
    else:
        o = 'PE'

    series='OPTSTK'
    if 'NIFTY' in instrument.get():
        series='OPTIDX'
    
    try :

        _, id_ = get_instru_id(instrument.get(),o,expiry.get(),st1.get(),series)
        print("ID ",id_)
        m  = MarketApi()
        m_bid, m_ask = m.get_quote(id_,2,1502)

        Bid_label['text'] = f"{m_bid[0]:.2f}"
        Ask_label['text'] = f"{m_ask[0]:.2f}"
    except Exception as e:
        print(e)
        messagebox.showerror("Error","Oops, something went wrong.\nTry again.")
        return 0
        
    
def sys_login():

    def login():
        try:
            mp = MarketApi()
            mp.login()
            mp.logini()
        except Exception as e:
            messagebox.showerror("Login Error",str(e))
    t = Thread(target=login,args=())
    t.start()

###-main_###

root = Tk()
root.geometry("950x600")
root.title("AlgoApp")

try :

    start_orders = Thread(target=start_last_orders)
    start_orders.start()

except xlrd.biffh.XLRDError:
    print("Nothing to show")


menu = Menu(root)
submenu1 = Menu(menu,tearoff=0,activebackground='white',activeforeground="black")
submenu1.add_command(label="PreorderScreen",command=preorderscreen,)
submenu1.add_command(label="OrderScreen",command=ordermenuscreen)
submenu1.add_command(label="ManageTrade",command=tradescreen)
submenu1.add_command(label="Login",command=sys_login)
menu.add_cascade(menu=submenu1,label="Options")
menu.add_command(label="Api",command=order_api)


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
instu = StringVar()
expiry = StringVar()


### Variables Order
total_active = 4
bs1 = IntVar()
bs2 = IntVar()
bs3 = IntVar()
bs4 = IntVar()

instru1 = StringVar()
instru2 = StringVar()
instru3 = StringVar()
instru4 = StringVar()

otype1 = IntVar()
otype2 = IntVar()
otype3 = IntVar()
otype4 = IntVar()

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

premium1 = IntVar()
premium2 = IntVar()
premium3 = IntVar()
premium4 = IntVar()

sdelta = IntVar()
tdelta = IntVar()

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
s1b = Radiobutton(orderframe, variable=bs1,text='BUY',value=1,bg='white')
s1s = Radiobutton(orderframe, variable=bs1,text='SELL',value=0,bg='white')
s2b = Radiobutton(orderframe, variable=bs2,text='BUY',value=1,bg='white')
s2s = Radiobutton(orderframe, variable=bs2,text='SELL',value=0,bg='white')

s3b = Radiobutton(orderframe, variable=bs3,text='BUY',value=1,bg='white')
s3s = Radiobutton(orderframe, variable=bs3,text='SELL',value=0,bg='white')

s4b = Radiobutton(orderframe, variable=bs4,text='BUY',value=1,bg='white')
s4s = Radiobutton(orderframe, variable=bs4,text='SELL',value=0,bg='white')

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
s1p = Radiobutton(orderframe, variable=otype1,text="PUT",value=0,bg='white')
s1c = Radiobutton(orderframe, variable=otype1,text="CALL",value=1,bg='white')

s2p = Radiobutton(orderframe, variable=otype2,text="PUT",value=0,bg='white')
s2c = Radiobutton(orderframe, variable=otype2,text="CALL",value=1,bg='white')

s3p = Radiobutton(orderframe, variable=otype3,text="PUT",value=0,bg='white')
s3c = Radiobutton(orderframe, variable=otype3,text="CALL",value=1,bg='white')

s4p = Radiobutton(orderframe, variable=otype4,text="PUT",value=0,bg='white')
s4c = Radiobutton(orderframe, variable=otype4,text="CALL",value=1,bg='white')

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
# exp1.set(date_list)
# exp1.set_completion_list(date_list)

exp2['values']=date_list
# exp2.set(date_list)
# exp2.set_completion_list(date_list)

exp3['values']=date_list
# exp3.set(date_list)
# exp3.set_completion_list(date_list)

exp4['values']=date_list
# exp4.set(date_list)
# exp4.set_completion_list(date_list)
#
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
## Trade Management

set_top()
create_api_top()
root.mainloop()