from tkinter import *
from tkinter import messagebox
from initiative import *

class EntityFrame(Frame):

    def __init__(self,master,combatmanager):
        Frame.__init__(self,master)        
        self['bd']=1
        self['relief']='groove'
        self.combatmanager=combatmanager
        #Name
        Label(self,text="Name:").grid(row=0,column=0,sticky=W)
        self.name=Entry(self,width=15)
        self.name.grid(row=0,column=1)
        #Health
        Label(self,text="Health:").grid(row=1,column=0,sticky=W)
        self.health=Entry(self,width=10)
        self.health.grid(row=1,column=1,sticky=W)
        #Bonus
        self.bonus=IntVar()
        Label(self,text="Bonus:").grid(row=2,column=0,sticky=W)
        self.bonusEntry=Entry(self,textvariable=self.bonus,width=4)
        self.bonusEntry.grid(row=2,column=1,sticky=W)
        #Player
        self.player=BooleanVar()
        Label(self,text="Player:").grid(row=0,column=3,sticky=W)
        self.playerCheckbutton=Checkbutton(self,variable=self.player,command=self.playerCheckboxCallback)        
        self.playerCheckbutton.grid(row=0,column=4,sticky=W)
        #Roll
        self.roll=IntVar()
        Label(self,text="Roll:").grid(row=1,column=3,sticky=W)
        self.rollEntry=Entry(self,textvariable=self.roll,width=2,state="disabled")
        self.rollEntry.grid(row=1,column=4)
        #Amount
        self.amount=IntVar()
        self.amount.set(1)
        Label(self,text="Amount:").grid(row=2,column=3,sticky=W)
        self.amountSpinbox=Spinbox(self,textvariable=self.amount,from_=1,to=99,width=2)
        self.amountSpinbox.grid(row=2,column=4,sticky=E)
        #Save
        self.save=Button(self,text="Save",command=self.saveCallback)
        self.save.grid(row=3,column=3,sticky=W,padx=5,pady=5)
        #Destroy
        self.destroyButton=Button(self,text="x",command=self.destroyCallback)
        self.destroyButton.grid(row=3,column=4,sticky=E,padx=5,pady=5)

    def playerCheckboxCallback(self):
        if(self.player.get()):
            self.amount.set(1)
            self.amountSpinbox["state"]="disabled"
            self.rollEntry["state"]="normal"
        else:
            self.amountSpinbox["state"]="normal"
            self.rollEntry["state"]="disabled"

    def saveCallback(self):
        print("Coming soon")

    def destroyCallback(self):
        self.combatmanager.entities.remove(self)
        self.destroy()



class CombatManager():

    def __init__(self,master):
        self.queue=EntityQueue()
        self.started=False
        #Menu
        self.menu=Menu()
        self.menu.add_command(label="File")
        master.config(menu=self.menu)
        
        #frame containing entities
        self.canvasframe=Frame(master)
        self.canvasframe.grid(row=0,column=0,columnspan=2)

        self.canvas=Canvas(self.canvasframe,highlightthickness=0)
        self.frame=Frame(self.canvas)
        self.scrollbar=Scrollbar(self.canvasframe,command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.grid(row=0,column=1,sticky=N+S+E)
        self.canvas.grid(row=0,column=0)
        self.canvas.create_window((0,0),window=self.frame,anchor='nw')

        self.frame.bind("<Configure>",self.configureCanvas)

        self.entities=[]
        self.entities.append(EntityFrame(self.frame,self))
        self.entities[0].pack(padx=5,pady=5)

        

        #start and add buttons
        self.startButton=Button(master,text="Start",command=self.start)
        self.addButton=Button(master,text="+",command=self.add)
        self.startButton.grid(row=1,column=0,sticky=W,padx=5,pady=5)
        self.addButton.grid(row=1,column=1,sticky=E,padx=5,pady=5)

        #Text with scrollbar for displaying entityqueue
        self.textframe=Frame(master)
        self.textframe.grid(columnspan=4,row=0,column=3)
        self.textscrollbar=Scrollbar(self.textframe)
        self.textscrollbar.grid(row=0,column=1,sticky=N+S+E)
        self.text=Text(self.textframe,width=40,state=DISABLED,yscrollcommand=self.textscrollbar.set)
        self.text.grid(row=0,column=0)
        self.textscrollbar.config(command=self.text.yview)
        #self.text.grid(columnspan=4,row=0,column=3,padx=10,pady=10)

        #command line, run and next buttons
        Label(master,text="Command:").grid(row=1,column=3)
        self.commandEntry=Entry(master)
        self.commandEntry.grid(row=1,column=4,sticky=W)
        self.runButton=Button(master,text="Run",command=self.run)
        self.nextButton=Button(master,text="Next",command=self.next)
        self.runButton.grid(row=1,column=5,sticky=W)
        self.nextButton.grid(row=1,column=6)

    def configureCanvas(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=240,height=400)

    def add(self):
        e=EntityFrame(self.frame,self)
        e.pack(padx=5,pady=5)
        self.entities.append(e)

    def start(self):
        error=False
        #two passes: one to check if any errors popped up, if not: one to actually make and append
        #entities
        for e in self.entities:
            #health->regex nog afwerken
            #bonus
            try:                
                e.bonus.get()
                e.bonusEntry['background']='white'
            except ValueError:
                error=True
                e.bonusEntry['background']='red'
            #player
            if e.player.get():
                #roll
                try:
                    e.roll.get()
                    e.rollEntry['background']='white'
                except ValueError:
                    error=True
                    e.rollEntry['background']='red'
            else:
                #amount
                try:
                    e.amount.get()
                    e.amountSpinbox['background']='white'
                except ValueError:
                    error=True
                    e.amountSpinbox['background']='red'

        if error:
            messagebox.showwarning("Start","One or more entries contain errors.")
        else:
            #second pass
            for e in self.entities:
                if e.player.get():
                    self.queue.append(Entity(e.name.get(),e.bonus.get(),10,e.roll.get(),True))
                else:
                    for i in range(e.amount.get()):
                        self.queue.append(Entity(e.name.get()+" "+str(i+1),e.bonus.get(),10,dice.d20()))
            self.queue.sort()
            self.refresh()
            
                
            
    def run(self):
        pass

    def next(self):
        self.queue.incr()
        self.refresh()

    def refresh(self):
        self.text.config(state=NORMAL)
        self.text.delete(1.0,END)
        self.text.insert(END,self.queue)
        self.text.config(state=DISABLED)



master=Tk()
master.title("Combat Manager")
master.resizable(width=False,height=False)
cm=CombatManager(master)
master.mainloop()
