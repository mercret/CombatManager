from tkinter import *
from tkinter import filedialog

import os

class SettingsDialog(Toplevel):

    def __init__(self,master,settings):
        Toplevel.__init__(self,master)
        self.oldsettings=settings.copy()
        self.settings=settings.copy()
        
        self.title("Settings")
        self.transient(master)

        self.frame=Frame(self)

        #Fight Dir
        Label(self.frame,text='Fight Directory').grid(row=0,column=0,padx=5,pady=5)
        self.fightdirvar=StringVar()
        self.fightdirvar.trace('w',self.fightdirChange)                             
        Entry(self.frame,textvariable=self.fightdirvar).grid(row=0,column=1,padx=5,pady=5)
        Button(self.frame,text="Select",command=self.selectfightdirCallback).grid(row=0,column=2,padx=5,pady=5)
        #Entity Dir
        Label(self.frame,text='Entity Directory').grid(row=1,column=0,padx=5,pady=5)
        self.entitydirvar=StringVar()
        self.entitydirvar.trace('w',self.entitydirChange)
        
        Entry(self.frame,textvariable=self.entitydirvar).grid(row=1,column=1,padx=5,pady=5)
        Button(self.frame,text="Select",command=self.selectentitydirCallback).grid(row=1,column=2,padx=5,pady=5)
        #Players
        Label(self.frame,text='Player Files').grid(row=2,column=0,columnspan=4,padx=5,pady=5)
        self.playerlistbox=Listbox(self.frame)
        self.playerlistbox.grid(row=3,column=0,rowspan=2,columnspan=3,padx=5,pady=5,sticky=EW)
        Button(self.frame,text='+',command=self.addPlayerCallback,width=1).grid(row=3,column=3,padx=5,pady=5,sticky=E)
        Button(self.frame,text='-',command=self.removePlayerCallback,width=1).grid(row=4,column=3,padx=5,pady=5,sticky=E)
        
        #button frame
        self.buttonframe=Frame(self)
        Button(self.buttonframe,text='Accept',command=self.acceptCallback).grid(row=0,column=0,padx=5,pady=5)
        Button(self.buttonframe,text='Cancel',command=self.cancelCallback).grid(row=0,column=1,padx=5,pady=5)

        #initialize values
        self.fightdirvar.set(self.settings['fightdir'])
        self.entitydirvar.set(self.settings['entitydir'])
        for p in self.settings['playerfiles']:
            self.playerlistbox.insert(END,p)


        self.frame.pack(padx=5,pady=5)
        self.buttonframe.pack(padx=5,pady=5)
        self.grab_set()
        self.wait_window(self)        


    def fightdirChange(self,name,index,mode):
        self.settings['fightdir']=self.fightdirvar.get()

    def entitydirChange(self,name,index,mode):
        self.settings['entitydir']=self.entitydirvar.get()

    def selectfightdirCallback(self,event=None):
        fightdir=filedialog.askdirectory()
        if fightdir:
            self.fightdirvar.set(fightdir)
            self.settings['fightdir']=fightdir

    def selectentitydirCallback(self,event=None):
        entitydir=filedialog.askdirectory()
        if entitydir:
            self.entitydirvar.set(entitydir)
            self.settings['entitydir']=entitydir

    def addPlayerCallback(self,event=None):
        playerfile=filedialog.askopenfilename(initialdir=self.settings['entitydir'])
        if playerfile:
            self.playerlistbox.insert(END,playerfile)
            self.settings['playerfiles'].append(playerfile)

    def removePlayerCallback(self,event=None):
        self.settings['playerfiles'].remove(self.playerlistbox.get(ACTIVE))
        self.playerlistbox.delete(ANCHOR)
        

    def acceptCallback(self,event=None):
        #check if settings have changed        
        if self.oldsettings==self.settings:
            self.settings=None
        else:
            #create directories if necessary
            if not os.path.exists(self.settings['fightdir']):
                try:
                    os.mkdir(self.settings['fightdir'])
                except OSError:
                    messagebox.showerror('Create Directory','Could not create directory: '+self.settings['fightdir'])
            if not os.path.exists(self.settings['entitydir']):
                try:
                    os.mkdir(self.settings['entitydir'])
                except OSError:
                    messagebox.showerror('Create Directory','Could not create directory: '+self.settings['entitydir'])
                        
        self.withdraw()
        self.update_idletasks()
        self.master.focus_set()
        self.destroy()

    def cancelCallback(self,event=None):
        #return None to indicate no changes were made
        self.settings=None
        self.master.focus_set()
        self.destroy()
