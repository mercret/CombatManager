from tkinter import *
import dice

class RollDialog(Toplevel):

    def __init__(self,master,entities):
        Toplevel.__init__(self,master)
        self.title("Insert Rolls")
        self.transient(master)

        self.frame=Frame(self)
        #header
        Label(self.frame,text='Name',font="-weight bold").grid(row=0,column=0,padx=5,pady=5)
        Label(self.frame,text='Roll',font="-weight bold").grid(row=0,column=1,padx=5,pady=5)
        Label(self.frame,text='Bonus',font="-weight bold").grid(row=0,column=2,columnspan=2,padx=5,pady=5)
        Label(self.frame,text='Initiative',font="-weight bold").grid(row=0,column=4,columnspan=2,padx=5,pady=5)
        #body
        #show info from given entityframes, roll dice if auto, ask for roll if not
        self.focus=None
        self.rolls=None
        self.rollvars=[]
        i=0
        for e in entities:
            for j in range(e.amount.get()):
                #list of roll, bonus, initiative
                self.rollvars.append([IntVar() for k in range(3)])
                self.rollvars[i][0].trace('w',lambda name,index,mode,i=i:self.updateInitiative(i))
                self.rollvars[i][1].set(e.bonus.get())
                if e.amount.get()==1:
                    name=e.name.get()
                else:
                    name=e.name.get()+' '+str(j+1)
                Label(self.frame,text=name,width=10).grid(row=i+1,column=0,sticky=W,padx=5,pady=5)               
                if e.autoroll.get():
                    self.rollvars[i][0].set(dice.Dice.d20.roll())
                    Label(self.frame,textvariable=self.rollvars[i][0]).grid(row=i+1,column=1,sticky=E,padx=5,pady=5)
                else:
                    self.rollvars[i][2].set(self.rollvars[i][1].get())
                    entry=Entry(self.frame,textvariable=self.rollvars[i][0],width=2)
                    entry.grid(row=i+1,column=1,sticky=E,padx=5,pady=5)
                    if self.focus==None:
                        self.focus=entry
                #sign
                Label(self.frame,text='+').grid(row=i+1,column=2)
                #bonus
                Label(self.frame,textvariable=self.rollvars[i][1]).grid(row=i+1,column=3)
                Label(self.frame,text="=").grid(row=i+1,column=4)
                #result: initiative
                Label(self.frame,textvariable=self.rollvars[i][2]).grid(row=i+1,column=5)                
                i+=1

        #ok and cancel button in seperate frame
        buttonframe=Frame(self)
        self.okButton=Button(buttonframe,text="OK",command=self.okCallback)
        self.okButton.grid(row=0,column=0,sticky=EW,padx=5,pady=5)
        self.cancelButton=Button(buttonframe,text="Cancel",command=self.cancelCallback)
        self.cancelButton.grid(row=0,column=1,sticky=EW,padx=5,pady=5)

        #bind return and keypad enter key to ok
        self.bind("<Return>",self.okCallback)
        self.bind('<KP_Enter>',self.okCallback)

        self.frame.pack(padx=5,pady=5,fill='both',expand=1)
        buttonframe.pack(padx=5,pady=5)


        #disable parent window
        self.grab_set()

        #set focus
        if self.focus!=None:
            self.focus.focus()
            self.focus.selection_to(END)
        self.wait_window(self)        

    def okCallback(self,event=None):
        #validate
        for r in self.rollvars:
            try:
                r[0].get()
                if not dice.Dice.d20.isRoll(r[0].get()):
                    raise ValueError
            except (TclError, ValueError):
                self.focus.focus()
                self.focus.selection_to(END)
                return
        self.withdraw()
        self.update_idletasks()
        self.rolls=[r[0].get() for r in self.rollvars]
        self.cancelCallback()

    def cancelCallback(self):
        self.master.focus_set()
        self.destroy()

    def updateInitiative(self,i):
        try:
            self.rollvars[i][2].set(self.rollvars[i][0].get()+self.rollvars[i][1].get())
        except (ValueError,TclError):
            pass
