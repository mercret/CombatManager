from tkinter import *
import dice

class EntityFrame(Frame):

    def __init__(self,master,combatmanager):
        Frame.__init__(self,master)        
        self['bd']=1
        self['relief']='groove'
        self.master=master
        self.combatmanager=combatmanager
        #Name
        self.name=StringVar()
        Label(self,text="Name:").grid(row=0,column=0,sticky=W)
        self.nameEntry=Entry(self,width=15,textvariable=self.name)
        self.nameEntry.grid(row=0,column=1)
        #Health
        self.health=StringVar()
        self.health.set("1")
        Label(self,text="Health:").grid(row=1,column=0,sticky=W)
        self.healthEntry=Entry(self,width=10,textvariable=self.health)
        self.healthEntry.grid(row=1,column=1,sticky=W)
        #Bonus
        self.bonus=IntVar()
        Label(self,text="Bonus:").grid(row=2,column=0,sticky=W)
        self.bonusEntry=Entry(self,textvariable=self.bonus,width=4)
        self.bonusEntry.grid(row=2,column=1,sticky=W)
        #Index
        self.index=StringVar()
        self.indexLabel=Label(self,textvariable=self.index)
        self.indexLabel.grid(row=3,column=0,sticky=W)
        #Player
        self.player=BooleanVar()
        Label(self,text="Player:").grid(row=0,column=3,sticky=W)
        self.playerCheckbutton=Checkbutton(self,variable=self.player,command=self.playerCheckboxCallback)        
        self.playerCheckbutton.grid(row=0,column=4,sticky=W)
        #Autoroll
        self.autoroll=BooleanVar()
        self.autoroll.set(True)
        Label(self,text="Auto Roll:").grid(row=1,column=3,sticky=W)
        self.autorollCheckbutton=Checkbutton(self,variable=self.autoroll)
        self.autorollCheckbutton.grid(row=1,column=4,sticky=W)
        #Amount
        self.amount=IntVar()
        self.amount.set(1)
        Label(self,text="Amount:").grid(row=2,column=3,sticky=W)
        self.amountSpinbox=Spinbox(self,textvariable=self.amount,from_=1,to=99,width=2)
        self.amountSpinbox.grid(row=2,column=4,sticky=E)
        #Add to combat
        self.addToCombatButton=Button(self,text="Add To Combat",command=self.addToCombatCallback)
        if not self.combatmanager.started:
            self.addToCombatButton['state']='disabled'
        self.addToCombatButton.grid(row=3,column=1,sticky=EW,padx=5,pady=5)
        #Save
        self.saveButton=Button(self,text="Save",command=self.saveCallback)
        self.saveButton.grid(row=3,column=3,sticky=W,padx=5,pady=5)
        #Destroy
        self.destroyButton=Button(self,text="x",command=self.destroyCallback)
        self.destroyButton.grid(row=3,column=4,sticky=E,padx=5,pady=5)

    def playerCheckboxCallback(self):
        if(self.player.get()):
            self.amount.set(1)
            self.autoroll.set(False)
            self.amountSpinbox["state"]="disabled"
            self.autorollCheckbutton["state"]="disabled"
        else:
            self.amountSpinbox["state"]="normal"
            self.autorollCheckbutton["state"]="normal"

    #returns a dict usable to save to json format
    def toJson(self):
        d=dict()
        d['name']=self.name.get()
        d['health']=self.health.get()
        d['bonus']=self.bonus.get()
        d['player']=self.player.get()
        d['autoroll']=self.autoroll.get()
        d['amount']=self.amount.get()
        return d

    #saves a general description of a type of entity to file
    def saveCallback(self):
        self.combatmanager.saveEntityCallback(self)            

    def destroyCallback(self):
        self.combatmanager.entities.remove(self)
        self.combatmanager.updateIndices()
        self.destroy()

    def addToCombatCallback(self):
        self.combatmanager.addToCombat(self)

    def fillIn(self,entity):
        self.name.set(entity['name'])
        self.health.set(entity['health'])
        self.bonus.set(entity['bonus'])
        self.player.set(entity['player'])
        self.autoroll.set(entity['autoroll'])
        self.amount.set(entity['amount'])
        self.playerCheckboxCallback()

    def setIndex(self, index):
        self.index.set("#"+str(index+1))

    def hasError(self):
        error=False
        #health
        if dice.isHealth(self.health.get()):
            self.healthEntry['background']='white'
        else:
            error=True
            self.healthEntry['background']='red'                
        #bonus
        try:                
            self.bonus.get()
            self.bonusEntry['background']='white'
        except (ValueError,TclError):
            error=True
            self.bonusEntry['background']='red'
        #player
        if not self.player.get():
            #amount
            try:
                self.amount.get()
                self.amountSpinbox['background']='white'
            except (ValueError,TclError):
                error=True
                self.amountSpinbox['background']='red'
        return error
