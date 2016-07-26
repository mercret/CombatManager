from tkinter import *

from widgets.verticalscrolledframe import VerticalScrolledFrame


class EntityQueueFrame(VerticalScrolledFrame):
    def __init__(self, master, *args, **kw):
        VerticalScrolledFrame.__init__(self, master, *args, **kw)
        for i in range(0, 8):
            self.interior.columnconfigure(i, weight=1)
        self.containers=[]
        self.started = False

    def refresh(self, entityqueue):
        if not self.started:
            #header
            Label(self.interior, text='Round: {}'.format(entityqueue.round + 1)).grid(row=0, column=0, columnspan=8,
                                                                                      sticky=EW, pady=5)
            Label(self.interior, width=2).grid(row=1, column=0, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Nr", width=2).grid(row=1, column=1, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Name", width=15).grid(row=1, column=2, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Initiative").grid(row=1, column=3, columnspan=2, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Health", width=5).grid(row=1, column=5, columnspan=2, sticky=EW, padx=5, pady=5)
            Label(self.interior, text="Remove").grid(row=1, column=7, columnspan=2, sticky=EW, padx=5, pady=5)

            #array with containers
            for row in range(2,2*entityqueue.length,2):
                e=EntityContainer(self.interior,row)
                self.containers.append(e)

            self.started=True

        #entities added during play
        if len(self.containers)!=entityqueue.length:
            for i in range(entityqueue.length-len(self.containers)):
                e=EntityContainer(self.interior,2*(len(self.containers)+1))
                self.containers.append(e)
        #fill in details
        i=0
        for entity in entityqueue:
            self.containers[i].fillin(entityqueue.index,entity,entityqueue.position == entityqueue.index)
            i+=1

    def clear(self):
        VerticalScrolledFrame.clear(self)
        self.containers=[]
        self.started=False



class EntityContainer():
    def __init__(self, master,row):
        #arrow
        self.arrow=StringVar()
        Label(master, textvariable=self.arrow, width=2) \
            .grid(row=row, column=0, sticky=EW, padx=5,pady=5, rowspan=2)
        # index
        self.index=StringVar()
        Label(master, textvariable=self.index, width=2) \
            .grid(row=row, column=1, sticky=EW, padx=5,pady=5, rowspan=2)
        # name
        self.name = StringVar()
        Label(master, textvariable=self.name, width=15) \
            .grid(row=row, column=2, sticky=EW, padx=5,pady=5, rowspan=2)
        # initiative
        self.initiative=StringVar()
        Label(master, textvariable=self.initiative, width=2) \
            .grid(row=row, column=3, sticky=EW, padx=5,pady=5, rowspan=2)
        Button(master, text='\u2191').grid(row=row, column=4, sticky=EW, padx=5)
        Button(master, text='\u2193').grid(row=row+1, column=4, sticky=EW, padx=5)
        # health
        self.health=StringVar()
        Label(master, textvariable=self.health, width=5) \
            .grid(row=row, column=5, sticky=EW, padx=5,pady=5, rowspan=2)
        Button(master, text="+").grid(row=row, column=6, sticky=EW, padx=5)
        Button(master, text="-").grid(row=row+1, column=6, sticky=EW, padx=5)
        # remove
        Button(master, text="X").grid(row=row, column=7, rowspan=2, columnspan=2, sticky=NSEW, padx=5)

    def fillin(self, index, entity, arrow):
        self.entity=entity

        self.arrow.set('\u2192' if arrow else '')
        self.index.set('{}'.format(index+1))
        self.name.set('{}'.format(entity.name))
        self.initiative.set('{:2.0f}'.format(entity.initiative))
        self.health.set('{:2}/{:2}'.format(entity.health, entity.maxHealth))




