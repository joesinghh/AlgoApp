from tkinter import *
from datetime import datetime
from threading import Thread, Event
from APIs import MarketApi
from tkinter import messagebox
import threading


## y coordinates
thread1 = Event()
thread2 = Event()
thread3 = Event()
events = [thread1, thread2, thread3]
total_threads = [0 ,0 ,0]


mp = MarketApi()
y1 = 120
y2 = 220
y3 = 320
""" Functions Threads """

def reset_events(event):
    event.reset()

def cmp(esegment):
    mp.getsymbol(1,"EQ",esegment)
    mp.get_quote()
    # print(mp.quote)
    bid = mp.bidinfo['Price']
    ask = mp.askinfo['Price']
    t = threading.enumerate()
    print(esegment, bid, ask, len(t)-1)

    return (bid, ask)

def get_cmp(s):
    
    if s==1:
        e1 = esegment1.get()
        data = cmp(e1)
        cprice1['text']= str(data[bs1.get()])
    elif s==2:
        e2 = esegment2.get()
        data = cmp(e2)
        cprice2['text']= str(data[bs2.get()])
    elif s==3:
        e3 = esegment3.get()
        data = cmp(e3)
        cprice3['text']= str(data[bs3.get()])
    
    if events[s-1].isSet() and total_threads[s-1] == 1:
        root.after(60000,get_cmp, s)
    else:
        print(s , "Ended")
        total_threads[s-1]-=1
        return

""" Functions Widget"""

def start():
    mainframe.tkraise()


def apply_function():
    i =0
    e1 = esegment1.get()
    e2 = esegment2.get()
    e3 = esegment3.get()

    if e1!="None":
        i=1
        total_threads[0]+=1
        thread1.set()
        t1 = Thread(target=get_cmp,args=(1,))
        t1.start()

    if e2!="None":
        total_threads[1]+=1
        thread2.set()
        i = 1
        t2 = Thread(target=get_cmp,args=(2,))
        t2.start()

    if e3!="None":
        total_threads[2]+=1
        thread3.set()
        i = 1
        t3 = Thread(target=get_cmp,args=(3,))
        t3.start()

    if i == 0:
        messagebox.showerror("Error","Nothing selected")

    # else:
    #     messagebox.showinfo("Info","Submit to start execution.")
    


""" main """
root =Tk()
root.geometry("800x600")
root.resizable(1,1)
root.title("AlgoApp")


""" Frames """
startframe = Frame(root)
mainframe = Frame(root)
startframe.place(relheight=1,relwidth=1)
mainframe.place(relheight=1,relwidth=1)
startframe.tkraise()


""" Variables """
sop = IntVar()
## section 1
active1 = IntVar()
active1.set(0)
bs1 = IntVar()
# bs1.set(1)
esegment1 = StringVar()
q1 = IntVar()
cm1 = ""
exdate1 = StringVar()
sprice1 = IntVar()

## section 2
active2 = IntVar()
active2.set(0)
bs2 = IntVar()
bs2.set(1)
esegment2 = StringVar()
q2 = IntVar()
cm2 = ""
exdate2 = StringVar()
sprice2 = IntVar()

## section3
active3 = IntVar()
active3.set(0)
bs3 = IntVar()
bs3.set(0)
esegment3 = StringVar()
q3 = IntVar()
cm3 = ""
exdate3 = StringVar()
sprice3 = IntVar()

""" startframe - widgets"""

sbutton = Button(startframe, text = "Start", command= start)
sbutton.pack()

""" MainFrame - widgets """

## radio buttons
radiob1 = Radiobutton(mainframe, value = 0, variable=bs1, text="Buy",font=("Arial",13))
radios1 = Radiobutton(mainframe, value = 1, variable=bs1, text="Sell",font=("Arial",13))

radiob2 = Radiobutton(mainframe, value = 0, variable=bs2, text="Buy",font=("Arial",13))
radios2 = Radiobutton(mainframe, value = 1, variable=bs2, text="Sell",font=("Arial",13))

radiob3 = Radiobutton(mainframe, value = 0, variable=bs3, text="Buy",font=("Arial",13))
radios3 = Radiobutton(mainframe, value = 1, variable=bs3, text="Sell",font=("Arial",13))

Label(mainframe, text="Buy/Sell").place(x=50, y=40)
radiob1.place(x=35,y=y1,)
radios1.place(x=100,y=y1)

radiob2.place(x=35,y=y2,)
radios2.place(x=100,y=y2)

radiob3.place(x=35,y=y3,)
radios3.place(x=100,y=y3)

## ComboBox
options = ("None",'RELIANCE','NIFTY','FSL')
esegment1.set(options[0])
esegment2.set(options[0])
esegment3.set(options[0])

cbox1 = OptionMenu(mainframe, esegment1,*options,)
cbox1.config(font = ("Arial",11))


cbox2 = OptionMenu(mainframe,  esegment2,*options)
cbox2.config(font = ("Arial",11))

cbox3 = OptionMenu(mainframe,  esegment3,*options)
cbox3.config(font = ("Arial",11))

Label(mainframe, text="Exchange \nSegment").place(x=195,y=40)
cbox1.place(x=175,y=y1,width=130,height = 30)
cbox2.place(x=175,y=y2,width=130,height = 30)
cbox3.place(x=175,y=y3,width=130,height = 30)
## Entries

sentry1 = Entry(mainframe, textvariable=sprice1,font=("Arial",12))
sentry2 = Entry(mainframe, textvariable=sprice2,font=("Arial",12))
sentry3 = Entry(mainframe, textvariable=sprice3,font=("Arial",12))

Label(mainframe, text="Strike \nPrice").place(x = 350,y=40)
sentry1.place(x=330,y=y1,width=80,height=30)
sentry2.place(x=330,y=y2,width=80,height=30)
sentry3.place(x=330,y=y3,width=80,height=30)


qty1 = Entry(mainframe, textvariable=q1,font=("Arial",12))
qty2 = Entry(mainframe, textvariable=q2,font=("Arial",12))
qty3 = Entry(mainframe, textvariable=q3,font=("Arial",12))

Label(mainframe, text='Quantity').place(x=565,y=40)
qty1.place(x=550, y=y1,width=70,height=30)
qty2.place(x=550, y=y2,width=70,height=30)
qty3.place(x=550, y=y3,width=70,height=30)


edate1 = Entry(mainframe, textvariable=exdate1,font=("Arial",12))
edate2 = Entry(mainframe, textvariable=exdate2,font=("Arial",12))
edate3 = Entry(mainframe, textvariable=exdate3,font=("Arial",12))

Label(mainframe, text='Expiry Date').place(x=450,y=40)
edate1.place(x = 430, y=y1, width=100,height=30)
edate2.place(x = 430, y=y2, width=100,height=30)
edate3.place(x = 430, y=y3, width=100,height=30)

## Labels

cprice1 = Label(mainframe, text=cm1, bg='red')
cprice2 = Label(mainframe, text=cm2,bg = 'red')
cprice3 = Label(mainframe, text=cm3, bg='red')

Label(mainframe, text='Current\n Price').place(x=660,y=40)
cprice1.place(x=640, y = y1, width=110,height=30)
cprice2.place(x=640, y = y2, width=110,height=30)
cprice3.place(x=640, y = y3, width=110,height=30)

## SOP

sopentry = Entry(mainframe, textvariable=sop)

## apply button

apply = Button(mainframe, text="APPLY",command=apply_function)
apply.place(x=250,y=500)

## Submit button

submit = Button(mainframe, text='SUBMIT')
submit.place(x=350,y=500)

root.mainloop()