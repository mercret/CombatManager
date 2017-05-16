from tkinter import *
import tkinter.font

from objects.dice import *

class DiceDialog(Toplevel):

    def __init__(self,master):
        Toplevel.__init__(self,master)

        self.largefont = tkinter.font.Font(size=20)

        self.title("Die Roll")

        Label(self,text="Dice").grid(row=0,column=0,padx=5,pady=5)
        self.dievar=StringVar()
        self.entry=Entry(self,textvariable=self.dievar)
        self.entry.bind("<Return>",self.rollCallback)
        self.entry.bind("<KP_Enter>",self.rollCallback)
        self.entry.grid(row=0,column=1,padx=5,pady=5)
        Button(self,text="Roll",command=self.rollCallback).grid(row=0,column=2,padx=5,pady=5)

        self.rollvar=StringVar()
        Label(self,textvariable=self.rollvar,bd=1,relief="ridge",width=3,font=self.largefont).grid(row=1,column=1,padx=5,pady=5)

        Button(self,text="Close",command=self.closeCallback).grid(row=2,column=1,padx=5,pady=5)




    def rollCallback(self,event=None):
        if isRoll(self.dievar.get()):
            self.entry.configure(bg="white")
            self.rollvar.set(str(getRoll(self.dievar.get())))
        else:
            self.entry.configure(bg="red")

    def closeCallback(self,event=None):
        self.master.focus_set()
        self.destroy()