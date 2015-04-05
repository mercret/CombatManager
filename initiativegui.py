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
        self.name=StringVar()
        Label(self,text="Name:").grid(row=0,column=0,sticky=W)
        self.nameEntry=Entry(self,width=15,textvariable=self.name)
        self.nameEntry.grid(row=0,column=1)
        #Health
        self.health=StringVar()
        Label(self,text="Health:").grid(row=1,column=0,sticky=W)
        self.healthEntry=Entry(self,width=10,textvariable=self.health)
        self.healthEntry.grid(row=1,column=1,sticky=W)
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

    def fillIn(self,name='',health='',bonus=0,player=False,):
        self.name.set(name)
        self.health.set(health)
        self.bonus.set(bonus)
        self.player.set(player)
        self.playerCheckboxCallback()

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
        except ValueError:
            error=True
            self.bonusEntry['background']='red'
        #player
        if self.player.get():
            #roll
            try:
                self.roll.get()
                self.rollEntry['background']='white'
            except ValueError:
                error=True
                self.rollEntry['background']='red'
        else:
            #amount
            try:
                self.amount.get()
                self.amountSpinbox['background']='white'
            except ValueError:
                error=True
                self.amountSpinbox['background']='red'
        return error
        



class CombatManager():

    def __init__(self,master):
        self.queue=EntityQueue()
        self.started=False
        #Menu
        self.menubar=Menu(master)
        self.filemenu=Menu(self.menubar,tearoff=0)
        self.filemenu.add_command(label="Load Player File",command=self.loadplayers)
        self.menubar.add_cascade(label="File",menu=self.filemenu)
        
        master.config(menu=self.menubar)
        
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
        self.command=StringVar()
        Label(master,text="Command:").grid(row=1,column=3)
        self.commandEntry=Entry(master,textvariable=self.command)
        self.commandEntry.bind('<Return>',self.run)
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
            if e.hasError():
                error=True
        if error:
            messagebox.showwarning("Start","One or more entries contain errors.")
        else:
            if self.started:
                if messagebox.askyesno("Start","Are you sure you  want to restart combat? Progress will be lost."):
                    self.queue.clear()
                else:
                    return
            else:
                self.started=True
            #second pass
            for e in self.entities:
                if e.player.get():
                    self.queue.append(Entity(e.name.get(),e.bonus.get(),dice.getHealth(e.health.get()),e.roll.get(),True))
                else:
                    if e.amount.get()==1:
                        self.queue.append(Entity(e.name.get(),e.bonus.get(),dice.getHealth(e.health.get()),dice.d20()))
                    else:
                        for i in range(e.amount.get()):
                            self.queue.append(Entity(e.name.get()+" "+str(i+1),e.bonus.get(),dice.getHealth(e.health.get()),dice.d20()))
            self.queue.sort()
            self.refresh()
            
    def run(self,event=None):
        command=self.command.get()
        command=command.split()
        if len(command)==0:
            pass
        #usage: next
        #make the next active entity in the queue, the acting entity
        elif (command[0]==commands[0] or command[0]==shortcuts[0]) and len(command)==1:
            self.next()
        #usage: heal n hp
        #heals entity with index n hp points
        elif (command[0]==commands[1] or command[0]==shortcuts[1]) and len(command)==3:
            try:
                self.queue.heal(int(command[1]),int(command[2]))
                self.refresh()
            except (ValueError, IndexError):
                messagebox.showwarning("Run",'Not a valid number.')
        #usage: damage n hp
        #damages entity with index n hp points
        elif (command[0]==commands[2] or command[0]==shortcuts[2]) and len(command)==3:
            try:
                self.queue.damage(int(command[1]),int(command[2]))
                self.refresh()
            except (ValueError, IndexError):
                messagebox.showwarning("Run",'Not a valid number.')
        #usage: remove n
        #remove entity with number n from queue        
        elif (command[0]==commands[3] or command[0]==shortcuts[3]) and len(command)==2:
            try:
                self.queue.remove(int(command[1]))
                self.refresh()
            except (ValueError, IndexError):
                messagebox.showwarning("Run",'Not a valid number.')
        #usage: restore n
        #revive a perviously removed entity from the queue
        elif (command[0]==commands[4] or command[0]==shortcuts[4]) and len(command)==2:
            try:
                self.queue.restore(int(command[1]))
                self.refresh()
            except (ValueError,IndexError):
                messagebox.showwarning("Run",'Not a valid number.')
        #usage: delay n
        #substract n from current entity. n can be negative.
        elif (command[0]==commands[5] or command[0]==shortcuts[5]) and len(command)==2:
            try:
                self.queue.delay(int(command[1]))
                self.refresh()
            except ValueError:
                messagebox.showwarning("Run",'Not a valid number.')

        elif (command[0]==commands[6] or command[0]==shortcuts[6]) and len(command)==1:
            s=helpdict['help']+'\nCommands:\n'
            for i in commands:
                s+=i+'\n'
            messagebox.showinfo("Help",s)
        elif(command[0]==commands[6] or command[0]==shortcuts[6]) and len(command)==2:
            try:
                messagebox.showinfo("Help",helpdict[command[1]])
            except KeyError:
                s='Not a command\nCommands:\n'
                for i in commands:
                    s+=i+'\n'
                messagebox.showinfo("Help",s)
        else:
            messagebox.showwarning("Run",'Unknown Command or Wrong Syntax.')
        #check if there are any enemies left
        if self.queue.activeEnemies()==0 and self.started:
            messagebox.showinfo("Run",'All enemies defeated.')
        self.command.set('')

    def next(self):
        self.queue.incr()
        self.refresh()

    def refresh(self):
        self.text.config(state=NORMAL)
        self.text.delete(1.0,END)
        self.text.insert(END,self.queue)
        self.text.config(state=DISABLED)

    def loadplayers(self):
        print('Coming soon')


master=Tk()
master.title("Combat Manager")
master.resizable(width=False,height=False)
cm=CombatManager(master)
cm.entities[0].fillIn('Mathias','10',2,True)
cm.add()
cm.entities[1].fillIn('Goblin','3d4+2',1,False)
master.mainloop()
