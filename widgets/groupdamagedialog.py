from tkinter import *


class GroupDamageDialog(Toplevel):

    def __init__(self,master,entityqueue):
        Toplevel.__init__(self,master)
        self.entityqueue=entityqueue

        self.title("Group Damage")
        self.transient(master)

        self.frame=Frame(self)
        Label(self.frame,text="Damage").grid(row=0,column=0,sticky=W,padx=5,pady=5)
        self.damagevar=IntVar()
        Entry(self.frame,textvariable=self.damagevar).grid(row=0,column=1,sticky=W,padx=5,pady=5)

        i=2
        for e in self.entityqueue:
            print(e)
            Label(self.frame,text=e.name).grid(row=i,column=0, sticky=W,padx=5,pady=5)
            

            i+=1

        self.frame.pack(padx=5,pady=5,fill='both',expand=1)

