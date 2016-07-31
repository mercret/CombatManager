from tkinter import *
import tkinter.font
from commands.commands import *

from widgets.verticalscrolledframe import VerticalScrolledFrame


class EntityQueueFrame(VerticalScrolledFrame):
    def __init__(self, master, combatmanager):
        VerticalScrolledFrame.__init__(self, master)
        self.combatmanager=combatmanager
        for i in [0,1,2,3,5]:
            self.interior.columnconfigure(i, weight=1)
        self.containers=[]
        self.started = False
        self.round=StringVar()
        self.interior['bg']='white'
        self.canvas['bg']='white'

        self.boldfont = tkinter.font.Font(weight=tkinter.font.BOLD)

    def refresh(self):
        if not self.started:
            #header

            Label(self.interior, textvariable=self.round,bg='white',font=self.boldfont) \
                .grid(row=0, column=0, columnspan=8,  sticky=EW, pady=5)
            Label(self.interior, text="Active",bg='white',font=self.boldfont) \
                .grid(row=1, column=0, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Nr", width=2,bg='white',font=self.boldfont) \
                .grid(row=1, column=1, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Name", width=15,bg='white',font=self.boldfont) \
                .grid(row=1, column=2, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Initiative",bg='white',font=self.boldfont) \
                .grid(row=1, column=3, columnspan=2, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Health", width=5,bg='white',font=self.boldfont) \
                .grid(row=1, column=5, columnspan=2, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Remove/\nRestore",bg='white',font=self.boldfont) \
                .grid(row=1, column=7, columnspan=2, sticky=EW, padx=5, pady=5)

            #array with containers
            for row in range(2,3*self.combatmanager.queue.length,3):
                e=EntityContainer(self.interior,row,self.combatmanager)
                self.containers.append(e)
                Frame(self.interior).grid(pady=5)

            self.started=True

        #entities added during play
        if len(self.containers)!=self.combatmanager.queue.length:
            for i in range(self.combatmanager.queue.length-len(self.containers)):
                e=EntityContainer(self.interior,3*(len(self.containers)+1),self.combatmanager)
                self.containers.append(e)
                Frame(self.interior).grid(pady=5)

        #fill in details
        i=0
        for entity in self.combatmanager.queue:
            self.containers[i].fillin(self.combatmanager.queue.index,entity,self.combatmanager.queue.position == self.combatmanager.queue.index)
            i+=1
        self.round.set('Round: {}'.format(self.combatmanager.queue.round+1))

    def clear(self):
        VerticalScrolledFrame.clear(self)
        self.containers=[]
        self.started=False
        self.interior['bg'] = 'white'
        for i in [0,1,2,3,5]:
            self.interior.columnconfigure(i, weight=1)



class EntityContainer():
    def __init__(self, master,row, combatmanager):
        self.boldfont = tkinter.font.Font(weight=tkinter.font.BOLD)
        self.combatmanager=combatmanager
        #arrow
        self.arrow=StringVar()
        Label(master, textvariable=self.arrow, width=2,bg='white',font=self.boldfont) \
            .grid(row=row, column=0, sticky=EW, padx=5,pady=5, rowspan=2)
        # index
        self.index=StringVar()
        Label(master, textvariable=self.index, width=2,bg='white') \
            .grid(row=row, column=1, sticky=EW, padx=5,pady=5, rowspan=2)
        # name
        self.name = StringVar()
        Label(master, textvariable=self.name, width=15,bg='white') \
            .grid(row=row, column=2, sticky=EW, padx=5,pady=5, rowspan=2)
        # initiative
        self.initiative=StringVar()
        Label(master, textvariable=self.initiative, width=2,bg='white') \
            .grid(row=row, column=3, sticky=EW, padx=5,pady=5, rowspan=2)
        self.upButton=Button(master, text='\u2191',command=self.delayUpCallback)
        self.upButton.grid(row=row, column=4, sticky=EW, padx=5)
        self.downButton=Button(master, text='\u2193',command=self.delayDownCallback)
        self.downButton.grid(row=row+1, column=4, sticky=EW, padx=5)
        # health
        self.health=StringVar()
        Label(master, textvariable=self.health, width=5,bg='white') \
            .grid(row=row, column=5, sticky=EW, padx=5,pady=5, rowspan=2)
        Button(master, text="+",command=self.healCallback).grid(row=row, column=6, sticky=EW, padx=5)
        Button(master, text="-",command=self.damageCallback).grid(row=row+1, column=6, sticky=EW, padx=5)
        # remove
        Button(master, text="X",command=self.removeCallback).grid(row=row, column=7, rowspan=2, columnspan=2, sticky=NSEW, padx=5)

    def fillin(self, index, entity, arrow):
        self.pos=index
        self.entity=entity
        if not entity.active:
            self.arrow.set('X')
        else:
            self.arrow.set('\u2192' if arrow else '')
        self.index.set('{}'.format(index+1))
        self.name.set('{}'.format(entity.name))
        self.initiative.set('{:2.0f}'.format(entity.initiative))
        self.health.set('{:2}/{:2}'.format(entity.health, entity.maxHealth))

        if self.pos==0:
            self.upButton['state']='disable'
        if self.pos==self.combatmanager.queue.length-1:
            self.downButton['state']='disable'

    def delayDownCallback(self):
        self.combatmanager.executeCommand(DelayCommand(self.combatmanager.queue,self.pos,True))

    def delayUpCallback(self):
        self.combatmanager.executeCommand(DelayCommand(self.combatmanager.queue,self.pos,False))

    def damageCallback(self):
        self.combatmanager.executeCommand(DamageCommand(self.combatmanager.queue,self.pos,1))

    def healCallback(self):
        self.combatmanager.executeCommand(HealCommand(self.combatmanager.queue,self.pos,1))

    def removeCallback(self):
        if self.entity.active:
            self.combatmanager.executeCommand(RemoveCommand(self.combatmanager.queue,self.pos))
        else:
            self.combatmanager.executeCommand(RestoreCommand(self.combatmanager.queue,self.pos))



