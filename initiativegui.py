from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import Combobox
import tkinter.font
from initiative import *
import json

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
        if self.name.get()=="":
            messagebox.showwarning("Save","No name given.")
            return
        try:
            filename=self.name.get()+".json"
            f=open(filename,'w')
            d=dict()
            d['name']=self.name.get()
            d['health']=self.health.get()
            d['bonus']=self.bonus.get()
            d['player']=self.player.get()
            json.dump(d,f)
            f.close()
            messagebox.showinfo("Save","Entity saved as "+filename)
        except OSError:
            messagebox.showerror("Save","Could not save file")
            
            

    def destroyCallback(self):
        self.combatmanager.entities.remove(self)
        self.combatmanager.updateIndices()
        self.destroy()

    def fillIn(self,entity):
        self.name.set(entity['name'])
        self.health.set(entity['health'])
        self.bonus.set(entity['bonus'])
        self.player.set(entity['player'])
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
        self.entities=[]
        self.queue=EntityQueue()
        self.started=False
        self.commandHistory=[]
        #Menu
        self.menubar=Menu(master)
        self.filemenu=Menu(self.menubar,tearoff=0)
        self.filemenu.add_command(label="Load Entity",command=self.loadEntityCallback)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Save Fight",command=self.saveFightCallback)
        self.filemenu.add_command(label="Load Fight",command=self.loadFightCallback)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit",command=self.exitCallback)
        
        self.menubar.add_cascade(label="Menu",menu=self.filemenu)        
        master.config(menu=self.menubar)
        
        #frame containing entities
        self.canvasframe=Frame(master)
        self.canvasframe.grid(row=0,column=0,columnspan=3)

        self.canvas=Canvas(self.canvasframe,highlightthickness=0)
        self.frame=Frame(self.canvas)
        
        #scrollbar
        self.scrollbar=Scrollbar(self.canvasframe,command=self.canvas.yview)
        self.scrollbar.grid(row=0,column=1,sticky=N+S+E)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        

        

        #self.entities.append(EntityFrame(self.frame,self))
        #self.entities[0].pack(padx=5,pady=5)
        
        self.canvas.grid(row=0,column=0)
        

        
        self.canvas.create_window((0,0),window=self.frame,anchor='nw')

        #workaround used to activate scrollbar
        self.frame.bind("<Configure>",self.configureCanvas)        
        self.configureCanvas(None)

        
        

        

        #start, add and load buttons
        self.startButton=Button(master,text="Start",command=self.startCallback)
        self.startButton.grid(row=1,column=0,sticky=EW,padx=5,pady=5)

        self.loadButton=Button(master,text="Load",command=self.loadEntityCallback)
        self.loadButton.grid(row=1,column=1,sticky=EW,padx=5,pady=5)
        
        self.addButton=Button(master,text="+",command=self.addCallback)
        self.addButton.grid(row=1,column=2,sticky=E,padx=5,pady=5)
        

        #Text with scrollbar for displaying entityqueue
        self.textframe=Frame(master)
        self.textframe.grid(columnspan=5,row=0,column=3)
        self.textscrollbar=Scrollbar(self.textframe)
        self.textscrollbar.grid(row=0,column=1,sticky=N+S+E)
        textfont=tkinter.font.nametofont("TkFixedFont")
        self.text=Text(self.textframe,width=35,state=DISABLED,yscrollcommand=self.textscrollbar.set,font=textfont.configure(size=14))
        self.text.grid(row=0,column=0)
        self.textscrollbar.config(command=self.text.yview)
        #self.text.grid(columnspan=4,row=0,column=3,padx=10,pady=10)

        #command line, run ,undo and next buttons
        self.command=StringVar()
        Label(master,text="Command:").grid(row=1,column=3)
        
        self.commandEntry=Combobox(master,textvariable=self.command,state='disabled',postcommand=self.updateHistory)
        self.commandEntry.bind('<Return>',self.runCallback)
        self.commandEntry.bind('<KP_Enter>',self.runCallback)
        self.commandEntry.grid(row=1,column=4,sticky=W)
        self.runButton=Button(master,text="Run",command=self.runCallback,state='disabled')
        self.runButton.grid(row=1,column=5,sticky=W)
        self.undoButton=Button(master,text="Undo",command=self.undoCallback,state='disabled')
        self.undoButton.grid(row=1,column=6)
        self.nextButton=Button(master,text="Next",command=self.nextCallback,state='disabled')
        self.nextButton.grid(row=1,column=7)
        
    def configureCanvas(self,event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"),width=300,height=400)

    def updateHistory(self):
        #use splicing to reverse list
        self.commandEntry.configure(values=['']+self.commandHistory[::-1])

    def addCallback(self):
        e=EntityFrame(self.frame,self)
        e.pack(padx=5,pady=5)
        index=len(self.entities)+1
        self.entities.append(e)
        e.index.set("#"+str(index))
        return e

    def updateIndices(self):
        for i in range(len(self.entities)):
            self.entities[i].index.set("#"+str(i+1))

    def startCallback(self):
        error=False
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
            else:
                self.started=True
                self.commandEntry['state']='normal'
                self.runButton['state']='normal'
                #self.undoButton['state']='normal'
                self.nextButton['state']='normal'
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

    #run command in commandline
    def runCallback(self,event=None):
        command=self.command.get()
        command=command.split()
        if len(command)==0:
            pass
        #usage: next
        #make the next active entity in the queue, the acting entity
        elif (command[0]==commands[0] or command[0]==shortcuts[0]) and len(command)==1:
            self.nextCallback()
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
            except (ValueError,IndexError):
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
        elif(command[0]==commands[7] or command[0]==shortcuts[7]) and len(command)==1:
            self.exitCallback()
        else:
            messagebox.showwarning("Run",'Unknown Command or Wrong Syntax.')
        #check if there are any enemies left
        if self.queue.activeEnemies()==0 and self.started:
            messagebox.showinfo("Run",'All enemies defeated.')
        self.commandHistory.append(self.command.get())
        self.command.set('')


    
    def nextCallback(self):
        self.queue.incr()
        self.refresh()

    def undoCallback(self):
        pass

    
    #refresh display of entityqueue
    def refresh(self):
        self.text.config(state=NORMAL)
        self.text.delete(1.0,END)
        self.text.insert(END,self.queue)
        self.text.config(state=DISABLED)

    #Menu items callback functions

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
                    l=[]
                    for e in self.queue.queue:
                        l.append(e.__dict__)
                    d["queue"]=l
                    json.dump(d,f)
                    f.close()
                    messagebox.showinfo("Save Fight","Fight saved as "+filename)
                except OSError:
                    messagebox.showerror("Save Fight","Could not save file")
        else:
            messagebox.showerror("Save Fight","No Active Fight")

            
            

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
                self.refresh()

                self.started=True
                self.commandEntry['state']='normal'
                self.runButton['state']='normal'
                #self.undoButton['state']='normal'
                self.nextButton['state']='normal'
            except OSError:
                messagebox.showerror('Load Fight','Could not open file '+filename)                
            except (KeyError,TypeError):
                messagebox.showerror('Load Fight','File '+filename+' not in correct format')                

                
            

    def exitCallback(self):
        if messagebox.askyesno("Exit","Are you sure you want to exit?"):
            master.destroy()
                
            


master=Tk()
master.title("Combat Manager")
master.resizable(width=False,height=False)
cm=CombatManager(master)
master.mainloop()
