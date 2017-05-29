from tkinter import *
import tkinter.font

from objects.dice import *


class DiceDialog(Toplevel):

    def __init__(self,master):
        Toplevel.__init__(self,master)


        self.title("Die Roll")
        self.resizable(False,False)
        self.largefont = tkinter.font.Font(size=20)
        self.largeunderlinefont= tkinter.font.Font(size=20,underline=True)

        Label(self,text="Dice").grid(row=0,column=0,padx=5,pady=5)
        self.dievar=StringVar()
        self.entry=Entry(self,textvariable=self.dievar,width=10)
        self.entry.bind("<Return>",self.rollCallback)
        self.entry.bind("<KP_Enter>",self.rollCallback)
        self.entry.grid(row=0,column=1,padx=5,pady=5)
        #roll button
        Button(self,text="Roll",command=self.rollCallback).grid(row=0,column=2,padx=5,pady=5)

        #frame containing one or two labels depending on selection
        self.rollframe=Frame(self)
        self.rollframe.grid(row=1,column=0,rowspan=3,columnspan=2)
        self.rollvar1=StringVar()
        self.rolllabel1=Label(self.rollframe,textvariable=self.rollvar1,bd=1,relief="ridge",width=3,font=self.largefont)
        self.rolllabel1.grid(row=0,column=0,padx=5,pady=5,sticky=EW)
        self.rollvar2=StringVar()
        self.rolllabel2=Label(self.rollframe,textvariable=self.rollvar2,bd=1,relief="ridge",width=3,font=self.largefont)
        self.rolllabels=(self.rolllabel1,self.rolllabel2)

        #radiobutton: none, advantage, disadvantage
        self.selectvar=IntVar()
        Radiobutton(self,text="None",variable=self.selectvar,value=0,command=self.selectcallback).grid(row=1,column=2,padx=5,pady=5,sticky=W)
        Radiobutton(self,text="Advantanage",variable=self.selectvar,value=1,command=self.selectcallback).grid(row=2,column=2,padx=5,pady=5,sticky=W)
        Radiobutton(self,text="Disadvantage",variable=self.selectvar,value=2,command=self.selectcallback).grid(row=3,column=2,padx=5,pady=5,sticky=W)

        #close button
        Button(self,text="Close",command=self.closeCallback).grid(row=4,column=0,columnspan=4,padx=5,pady=5)


    def selectcallback(self,event=None):
        if self.selectvar.get()==0:
            self.rolllabel1.config(font=self.largefont)
            self.rolllabel2.grid_forget()
        else:
            self.rolllabel2.grid(row=0,column=1,padx=5,pady=5,sticky=EW)

    def rollCallback(self,event=None):
        if isRoll(self.dievar.get()):
            self.entry.configure(bg="white")
            if self.selectvar.get()==0:
                self.rollvar1.set(str(getRoll(self.dievar.get())))
            else:
                rolls=(getRoll(self.dievar.get()),getRoll(self.dievar.get()))
                self.rollvar1.set(str(rolls[0]))
                self.rollvar2.set(str(rolls[1]))
                max=0 if rolls[0] > rolls[1] else 1
                if rolls[0]==rolls[1]:
                    self.rolllabel1.config(font=self.largeunderlinefont)
                    self.rolllabel2.config(font=self.largeunderlinefont)
                elif self.selectvar.get()==1:
                    self.rolllabels[max].config(font=self.largeunderlinefont)
                    self.rolllabels[1-max].config(font=self.largefont)
                elif self.selectvar.get()==2:
                    self.rolllabels[1-max].config(font=self.largeunderlinefont)
                    self.rolllabels[max].config(font=self.largefont)
        else:
            self.entry.configure(bg="red")

    def closeCallback(self,event=None):
        self.master.focus_set()
        self.destroy()