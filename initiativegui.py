from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import Combobox
import tkinter.font

from initiative import *
from command import *
import json

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
        if self.name.get()=="":
            messagebox.showwarning("Save","No name given.")
            return
        try:
            filename=self.name.get()+".json"
            f=open(filename,'w')
            d=self.toJson()
            d['amount']=1
            json.dump(d,f)
            f.close()
            messagebox.showinfo("Save","Entity saved as "+filename)
        except OSError:
            messagebox.showerror("Save","Could not save file")
            
            

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

class CombatManager(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title("Combat Manager")
        self.resizable(width=False,height=False)
        self.entities=[]
        self.queue=EntityQueue()
        self.started=False
        self.textcommandhistory=[]
        self.commandhistory=CommandHistory()
        #Menu
        self.menubar=Menu(self)
        self.filemenu=Menu(self.menubar,tearoff=0)
        self.filemenu.add_command(label="Load Entity",command=self.loadEntityCallback)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Save Fight",command=self.saveFightCallback,state="disable")
        self.filemenu.add_command(label="Load Fight",command=self.loadFightCallback)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit",command=self.exitCallback)
        
        
        self.menubar.add_cascade(label="Menu",menu=self.filemenu)        
        self.config(menu=self.menubar)
        
        #frame containing entities
        self.canvasframe=Frame(self,borderwidth=2,relief=RIDGE)
        self.canvasframe.grid(row=0,column=0,columnspan=4,sticky='nsew')
        self.canvasframe.rowconfigure(0,weight=1)

        self.canvas=Canvas(self.canvasframe,highlightthickness=0)
        self.frame=Frame(self.canvas)
        
        #scrollbar
        self.scrollbar=Scrollbar(self.canvasframe,command=self.canvas.yview)
        self.scrollbar.grid(row=0,column=1,sticky='nse')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0,column=0,sticky='nsew')       
        self.canvas.create_window((0,0),window=self.frame,anchor='nw')
        self.frame.bind("<Configure>",self.configureCanvas)

        #mousewheel events
        #windows
        self.canvas.bind("<MouseWheel>",lambda event: self.canvas.yview('scroll',int(-1*(event.delta/120)),'units'))
        #unix
        self.canvas.bind("<Button-4>",lambda event: self.canvas.yview('scroll',-1,'units'))
        self.canvas.bind("<Button-5>",lambda event: self.canvas.yview('scroll',1,'units'))                       

        #start, add, clear and load buttons
        self.startButton=Button(self,text="Start",command=self.startCallback)
        self.startButton.grid(row=1,column=0,sticky=EW,padx=5,pady=5)

        self.loadButton=Button(self,text="Load Entity",command=self.loadEntityCallback)
        self.loadButton.grid(row=1,column=1,sticky=EW,padx=5,pady=5)

        self.clearButton=Button(self,text="Clear", command=self.clearCallback)
        self.clearButton.grid(row=1,column=2,sticky=EW,padx=5,pady=5)
        
        self.addButton=Button(self,text="+",command=self.addCallback)
        self.addButton.grid(row=1,column=3,sticky=E,padx=5,pady=5)
        

        #Text with scrollbar for displaying entityqueue
        self.textframe=Frame(self)
        self.textframe.grid(columnspan=6,row=0,column=4)
        self.textscrollbar=Scrollbar(self.textframe)
        self.textscrollbar.grid(row=0,column=1,sticky=N+S+E)
        textfont=tkinter.font.nametofont("TkFixedFont")
        self.text=Text(self.textframe,height=32,width=40,state=DISABLED,yscrollcommand=self.textscrollbar.set,font=textfont.configure(size=14))
        self.text.grid(row=0,column=0)
        self.textscrollbar.config(command=self.text.yview)

        #command line, run ,undo, redo and next buttons
        self.commandstring=StringVar()
        Label(self,text="Command:").grid(row=1,column=4)
        
        self.commandEntry=Combobox(self,textvariable=self.commandstring,state='disabled',postcommand=self.updateHistory)
        self.commandEntry.bind('<Return>',self.runCallback)
        self.commandEntry.bind('<KP_Enter>',self.runCallback)
        self.commandEntry.grid(row=1,column=5,sticky=W)
        self.runButton=Button(self,text="Run",command=self.runCallback,state='disabled')
        self.runButton.grid(row=1,column=6,sticky=EW)
        self.undoButton=Button(self,text="Undo",command=self.undoCallback,state='disabled')
        self.undoButton.grid(row=1,column=7,sticky=EW)
        self.redoButton=Button(self,text="Redo",command=self.redoCallback,state='disabled')
        self.redoButton.grid(row=1,column=8,sticky=EW)
        self.nextButton=Button(self,text="Next",command=self.nextCallback,state='disabled')
        self.nextButton.grid(row=1,column=9,sticky=EW)

        
    def configureCanvas(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def updateHistory(self):
        #use splicing to reverse list
        self.commandEntry.configure(values=['']+self.textcommandhistory[::-1])

    def addCallback(self):
        e=EntityFrame(self.frame,self)
        e.pack(padx=5,pady=5)
        index=len(self.entities)
        self.entities.append(e)
        e.setIndex(index)
        return e

    def updateIndices(self):
        for i in range(len(self.entities)):
            self.entities[i].setIndex(i)
            
    #enables certain widgets on start
    def enableWidgetsOnStart(self):
        self.commandEntry['state']='normal'
        self.runButton['state']='normal'
        #self.undoButton['state']='normal'
        #self.redoButton['state']='normal'
        self.nextButton['state']='normal'
        for ef in self.entities:
            if not ef.player.get():
                ef.addToCombatButton['state']='normal'            
                #ef.autoroll.set(False)
        self.filemenu.entryconfig("Save Fight",state='normal')
        
    #disables certain widgets on stop
    def disableWidgetsOnStop(self):
        self.commandEntry['state']='disabled'
        self.runButton['state']='disabled'
        self.undoButton['state']='disabled'
        self.redoButton['state']='disabled'
        self.nextButton['state']='disabled'
        for ef in self.entities:
            if not ef.player.get():
                ef.addToCombatButton['state']='disabled'
                #ef.autoroll.set(True)
        self.filemenu.entryconfig("Save Fight",state='disable')



    def addToCombat(self,e):
        if e.hasError():
            messagebox.showwarning("Add Entity","One or more entries contain errors.")
            return
        rd=RollDialog(self,[e])
        if rd.rolls==None:
            return
        else:
            i=0
            for j in range(e.amount.get()):
                if e.amount.get()==1:
                    name=e.name.get()
                else:
                    name=e.name.get()+' '+str(j+1)
                self.queue.append(Entity(name,e.bonus.get(),dice.getHealth(e.health.get()),rd.rolls[i],e.player.get()))
                i+=1
                    
                        
            self.queue.sort()
            self.refreshDisplay()
            

    def startCallback(self):
        error=False
        if len(self.entities)==0:
            return
        #two passes: one to check if any errors popped up, if not: one to actually make entities and append
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
            #second pass
            rd=RollDialog(self,self.entities)
            if rd.rolls==None:
                return
            else:
                i=0
                for e in self.entities:
                    for j in range(e.amount.get()):
                        if e.amount.get()==1:
                            name=e.name.get()
                        else:
                            name=e.name.get()+' '+str(j+1)
                        self.queue.append(Entity(name,e.bonus.get(),dice.getHealth(e.health.get()),rd.rolls[i],e.player.get()))
                        i+=1
                        
                            
                self.queue.sort()
                self.refreshDisplay()

                self.enableWidgetsOnStart()
                self.started=True

    def nextCallback(self):
        command=NextCommand(self.queue)
        command.execute()
        self.commandhistory.append(command)
        self.checkCommandHistory()
        self.refreshDisplay()

    def runCallback(self,event=None):
        commandstring=self.commandstring.get()
        commandstring=commandstring.split()
        command=None
        if len(commandstring)==0:
            pass
        #usage: next
        #make the next active entity in the queue, the acting entity
        elif (commandstring[0]==commands[0] or commandstring[0]==shortcuts[0]) and len(commandstring)==1:
            command=NextCommand(self.queue)
        #usage: heal n hp
        #heals entity with index n hp points
        elif (commandstring[0]==commands[1] or commandstring[0]==shortcuts[1]) and len(commandstring)==3:
            try:
                command=HealCommand(self.queue,int(commandstring[1]),int(commandstring[2]))
            except ValueError:
                messagebox.showwarning("Run",'Not a valid number.')
        #usage: damage n hp
        #damages entity with index n hp points
        elif (commandstring[0]==commands[2] or commandstring[0]==shortcuts[2]) and len(commandstring)==3:
            try:
                command=DamageCommand(self.queue,int(commandstring[1]),int(commandstring[2]))
            except ValueError:
                messagebox.showwarning("Run",'Not a valid number.')
        #usage: remove n
        #remove entity with number n from queue        
        elif (commandstring[0]==commands[3] or commandstring[0]==shortcuts[3]) and len(commandstring)==2:
            try:
                command=RemoveCommand(self.queue,int(commandstring[1]))
            except ValueError:
                messagebox.showwarning("Run",'Not a valid number.')
        #usage: restore n
        #revive a previously removed entity from the queue
        elif (commandstring[0]==commands[4] or commandstring[0]==shortcuts[4]) and len(commandstring)==2:
            try:
                command=RestoreCommand(self.queue,int(commandstring[1]))
            except ValueError:
                messagebox.showwarning("Run",'Not a valid number.')
        #usage: delay n
        #substract n from current entity. n can be negative.
        elif (commandstring[0]==commands[5] or commandstring[0]==shortcuts[5]) and len(commandstring)==2:
            try:
                command=DelayCommand(self.queue,int(commandstring[1]))
            except ValueError:
                messagebox.showwarning("Run",'Not a valid number.')
        #help
        elif (commandstring[0]==commands[6] or commandstring[0]==shortcuts[6]) and len(commandstring)==1:
            s=helpdict['help']+'\nCommands:\n'
            for i in commands:
                s+=i+'\n'
            messagebox.showinfo("Help",s)
            return
        elif(commandstring[0]==commands[6] or commandstring[0]==shortcuts[6]) and len(commandstring)==2:
            try:
                messagebox.showinfo("Help",helpdict[commandstring[1]])
            except KeyError:
                s='Not a command\nCommands:\n'
                for i in commands:
                    s+=i+'\n'
                messagebox.showinfo("Help",s)
        #stop
        elif(commandstring[0]==commands[7] or commandstring[0]==shortcuts[7]) and len(commandstring)==1:
            self.exitCallback()
        else:
            messagebox.showwarning("Run",'Unknown Command or Wrong Syntax. Use help command for, you know, help.')

        #execute command
        if command is not None:
            try:
                command.execute()                
                self.refreshDisplay()
                self.commandhistory.append(command)
                self.checkCommandHistory()
                self.textcommandhistory.append(self.commandstring.get())
                self.commandstring.set('')
            except IndexError:
                messagebox.showwarning("Run","Index Out of Range.")

            #check if there are any enemies left
            if self.queue.activeEnemies()==0 and self.started:
                messagebox.showinfo("Run",'All enemies defeated.')

    def undoCallback(self):
        self.commandhistory.undo()
        self.checkCommandHistory()
        self.refreshDisplay()

    def redoCallback(self):
        self.commandhistory.redo()
        self.checkCommandHistory()
        self.refreshDisplay()

    def checkCommandHistory(self):
        #disable undo if at begin of commandhistory
        if self.commandhistory.atBegin():
            self.undoButton['state']='disabled'
        else:
            self.undoButton['state']='normal'
        #disable redo if at end of commandhistory
        if self.commandhistory.atEnd():
            self.redoButton['state']='disabled'
        else:
            self.redoButton['state']='normal'
    
    #refresh display of entityqueue
    def refreshDisplay(self):
        self.text.config(state=NORMAL)
        self.text.delete(1.0,END)
        self.text.insert(END,self.queue)
        self.text.config(state=DISABLED)

    #clear display of entityqueue
    def clearDisplay(self):
        self.text.config(state=NORMAL)
        self.text.delete(1.0,END)
        self.text.config(state=DISABLED)


    def loadEntityCallback(self):
        filenames=filedialog.askopenfilenames()
        for filename in filenames:
            try:
                f=open(filename,'r')
                d=json.load(f)
                f.close()
                e=self.addCallback()
                e.fillIn(d)                
            except OSError:
                messagebox.showerror('Load Entity','Could not open file '+filename)
                e.destroyCallback()
            except (KeyError,TypeError):
                messagebox.showerror('Load Entity','File '+filename+' not in correct format')
                e.destroyCallback()

    def clearCallback(self):
        self.queue.clear()
        self.commandhistory.clear()
        self.clearDisplay()
        for e in self.entities:
            e.destroy()
        self.entities=[]
        self.started=False
        self.disableWidgetsOnStop()

    def saveFightCallback(self):
        if self.started:
            filename=filedialog.asksaveasfilename(defaultextension=".json")
            if filename:
                try:
                    f=open(filename,'w')

                    d=dict()
                    d["position"]=self.queue.position
                    d["round"]=self.queue.round
                    #iterate over entities in EntityQueue and save their dictionary representation to a list
                    entitiesList=[]
                    for e in self.queue.queue:
                        entitiesList.append(e.__dict__)
                    d["queue"]=entitiesList
                    #iterate over EntityFrames and save their dictionary representation to a list
                    entityFramesList=[]
                    for ef in self.entities:
                        entityFramesList.append(ef.toJson())
                    d["frames"]=entityFramesList
                    json.dump(d,f)
                    f.close()
                    messagebox.showinfo("Save Fight","Fight saved as "+filename)
                except OSError:
                    messagebox.showerror("Save Fight","Could not save file")                       

    def loadFightCallback(self):
        if self.started:
            if not messagebox.askyesno("Start","Are you sure you  want to restart combat? Progress will be lost."):
                return
        filename=filedialog.askopenfilename()
        if filename:
            try:
                f=open(filename,'r')
                d=json.load(f)
                f.close()
                self.queue.clear()
                self.queue.position=d["position"]
                self.queue.round=d["round"]
                for e in d["queue"]:
                    self.queue.append(Entity.fromDict(e))
                self.queue.sort()
                self.refreshDisplay()
                for ef in d["frames"]:
                    e=self.addCallback()
                    e.fillIn(ef)

                self.started=True
                self.enableWidgetsOnStart()
            except OSError:
                messagebox.showerror('Load Fight','Could not open file '+filename)                
            except (KeyError,TypeError):
                messagebox.showerror('Load Fight','File '+filename+' not in correct format')                        

    def exitCallback(self):
        if messagebox.askyesno("Exit","Are you sure you want to exit?"):
            self.destroy()

cm=CombatManager()
cm.mainloop()
