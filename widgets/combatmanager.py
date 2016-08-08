import json
import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Combobox

from commands.helpmessages import *
from commands.commands import *
from objects import dice
from objects.entityqueue import *
from widgets.entityqueueframe import EntityQueueFrame
from widgets.entryframe import EntryFrame
from widgets.rolldialog import RollDialog
from widgets.settingsdialog import SettingsDialog
from widgets.verticalscrolledframe import VerticalScrolledFrame


class CombatManager(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Combat Manager")

        # allows row 0 (=frame, textframe) to expand vertically
        self.rowconfigure(0, weight=1)
        # allows columns starting with textframe to expand horizontally
        for i in range(4, 9):
            self.columnconfigure(i, weight=1)

        self.entities = []
        self.queue = EntityQueue()
        self.started = False
        self.textcommandhistory = []
        self.commandhistory = CommandHistory()
        self.names = dict()
        # Menu
        self.menubar = Menu(self)
        # File Menu
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load Entity", command=self.loadEntityCallback)
        self.filemenu.add_command(label="Load Players", command=self.loadPlayersCallback)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Save Fight", command=self.saveFightCallback, state="disable")
        self.filemenu.add_command(label="Load Fight", command=self.loadFightCallback)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Settings", command=self.settingsCallback)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.exitCallback)

        self.menubar.add_cascade(label="Menu", menu=self.filemenu)
        self.config(menu=self.menubar)

        #VerticalScrolledFrame containing EntityFrames
        self.frame=VerticalScrolledFrame(self,borderwidth=2,relief=RIDGE)
        self.frame.grid(row=0,column=0,columnspan=4,sticky=NSEW)



        # start, add, clear and load buttons
        self.startButton = Button(self, text="Start", command=self.startCallback)
        # self.startButton.grid(row=1,column=0,sticky=EW,padx=5,pady=5)
        self.startButton.grid(row=1, column=0, rowspan=2, sticky=NSEW, padx=5, pady=5)

        self.loadButton = Button(self, text="Load Entity", command=self.loadEntityCallback)
        # self.loadButton.grid(row=1,column=1,sticky=EW,padx=5,pady=5)
        self.loadButton.grid(row=1, column=1, rowspan=2, sticky=NSEW, padx=5, pady=5)

        self.clearButton = Button(self, text="Clear", command=self.clearCallback)
        # self.clearButton.grid(row=1,column=2,sticky=EW,padx=5,pady=5)
        self.clearButton.grid(row=1, column=2, rowspan=2, sticky=NSEW, padx=5, pady=5)

        self.addButton = Button(self, text="+", command=self.addCallback)
        # self.addButton.grid(row=1,column=3,sticky=E,padx=5,pady=5)
        self.addButton.grid(row=1, column=3, rowspan=2, sticky=NSEW, padx=5, pady=5)

        #EntityQueueuFrame containing the EntityQueue
        self.eqf=EntityQueueFrame(self,self)
        self.eqf.grid(row=0,column=4,columnspan=5,sticky=NSEW)


        # command line, run ,undo, redo and next buttons
        self.commandstring = StringVar()
        Label(self, text="Command:").grid(row=2, column=4,sticky=E)
        self.commandEntry = Combobox(self, textvariable=self.commandstring, state='disabled',
                                     postcommand=self.updateHistory)
        self.commandEntry.bind('<Return>', self.runCallback)
        self.commandEntry.bind('<KP_Enter>', self.runCallback)
        self.commandEntry.grid(row=2, column=5, sticky=EW)
        self.runButton = Button(self, text="Run", command=self.runCallback, state='disabled')
        self.runButton.grid(row=2, column=6, sticky=EW)
        self.undoButton = Button(self, text="Undo", command=self.undoCallback, state='disabled')
        self.undoButton.grid(row=2, column=7, sticky=EW)
        self.redoButton = Button(self, text="Redo", command=self.redoCallback, state='disabled')
        self.redoButton.grid(row=2, column=8, sticky=EW)

        self.nextButton = Button(self, text="Next", command=self.nextCallback, state='disabled')
        self.nextButton.grid(row=1, column=4, columnspan=5, sticky=EW)

        # General Key Bindings
        self.bind('<Control-q>', self.exitCallback)
        self.bind('<Control-z>', self.undoCallback)
        self.bind('<Control-Z>', self.redoCallback)
        self.bind('<Control-n>', self.nextCallback)
        self.bind('<Control-o>', self.loadFightCallback)
        self.bind('<Control-s>',self.saveFightCallback)
        self.bind('<Control-c>',self.focusCallback)

        # Load Settings
        self.loadSettings()

    def configureCanvas(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def updatename(self, name):
        for e in self.queue:
            if e.name == name:
                e.name = name + ' 1'

    def loadSettings(self):
        if os.path.exists('settings.json'):
            try:
                f = open('settings.json', 'r')
                self.settings = json.load(f)
                f.close()
            except OSError:
                messagebox.showerror('Load Settings', 'Could not load settings')
            except (KeyError, TypeError):
                messagebox.showerror('Load Settings', 'Settings file not in correct format')
        else:
            self.initializeSettings()

    def initializeSettings(self):
        currentdir = os.getcwd()
        self.settings = dict()
        self.settings['fightdir'] = currentdir
        self.settings['entitydir'] = currentdir
        self.settings['playerfiles'] = []
        try:
            f = open('settings.json', 'w')
            json.dump(self.settings, f)
            f.close()
        except OSError:
            messagebox.showerror("Save Settings", "Could not save settings")

    def updateHistory(self):
        # use splicing to reverse list
        self.commandEntry.configure(values=[''] + self.textcommandhistory[::-1])

    def addCallback(self):
        e = EntryFrame(self.frame.interior, self)
        e.pack(padx=5, pady=5)
        index = len(self.entities)
        self.entities.append(e)
        e.setIndex(index)
        return e

    def updateIndices(self):
        for i in range(len(self.entities)):
            self.entities[i].setIndex(i)

    # enables certain widgets on start
    def enableWidgetsOnStart(self):
        self.commandEntry['state'] = 'normal'
        self.runButton['state'] = 'normal'
        # self.undoButton['state']='normal'
        # self.redoButton['state']='normal'
        self.nextButton['state'] = 'normal'
        for ef in self.entities:
            if not ef.player.get():
                ef.addToCombatButton['state'] = 'normal'
                # ef.autoroll.set(False)
        self.filemenu.entryconfig("Save Fight", state='normal')

    # disables certain widgets on stop
    def disableWidgetsOnStop(self):
        self.commandEntry['state'] = 'disabled'
        self.runButton['state'] = 'disabled'
        self.undoButton['state'] = 'disabled'
        self.redoButton['state'] = 'disabled'
        self.nextButton['state'] = 'disabled'
        for ef in self.entities:
            if not ef.player.get():
                ef.addToCombatButton['state'] = 'disabled'
                # ef.autoroll.set(True)
        self.filemenu.entryconfig("Save Fight", state='disable')

    #external callbacks (=called from object other than combatmanager)
    def addToCombat(self, e):
        if e.hasError():
            messagebox.showwarning("Add Entity", "One or more entries contain errors.")
            return
        rd = RollDialog(self, [e], self.names)
        if rd.rolls == None:
            return
        else:
            i = 0
            entities = []
            for j in range(e.amount.get()):
                entities.append(
                    Entity(rd.names[i], e.bonus.get(), dice.getHealth(e.health.get()), rd.rolls[i], e.ac.get(), e.player.get()))
                i += 1

            command = AddCommand(self.queue, entities)
            self.executeCommand(command)

    def startCallback(self):
        error = False
        if len(self.entities) == 0:
            return
        # two passes: one to check if any errors popped up, if not: one to actually make entities and append
        # entities
        for e in self.entities:
            if e.hasError():
                error = True
        if error:
            messagebox.showwarning("Start", "One or more entries contain errors.")
        else:

            if self.started:
                if messagebox.askyesno("Start", "Are you sure you  want to restart combat? Progress will be lost."):
                    self.queue.clear()
                    self.names.clear()
                else:
                    return
            # second pass
            rd = RollDialog(self, self.entities, self.names)
            # print(self.names)
            if rd.rolls == None:
                return
            else:
                i = 0
                for e in self.entities:
                    for j in range(e.amount.get()):
                        self.queue.append(
                            Entity(rd.names[i], e.bonus.get(), dice.getHealth(e.health.get()), rd.rolls[i], e.ac.get(),e.player.get()))
                        i += 1

                #self.queue.sort()
                self.refreshDisplay()

                self.enableWidgetsOnStart()
                self.started = True

    def nextCallback(self, event=None):
        if self.started:
            command = NextCommand(self.queue)
            command.execute()
            self.commandhistory.append(command)
            self.checkCommandHistory()
            self.refreshDisplay()

    def runCallback(self, event=None):
        commandstring = self.commandstring.get()
        commandstring = commandstring.split()
        command = None
        if len(commandstring) == 0:
            pass
        # usage: next
        # make the next active entity in the queue, the acting entity
        elif (commandstring[0] == commands[0] or commandstring[0] == shortcuts[0]) and len(commandstring) == 1:
            command = NextCommand(self.queue)
        # usage: heal n hp
        # heals entity with index n hp points
        elif (commandstring[0] == commands[1] or commandstring[0] == shortcuts[1]) and len(commandstring) == 3:
            try:
                command = HealCommand(self.queue, int(commandstring[1])-1, int(commandstring[2]))
            except ValueError:
                messagebox.showwarning("Run", 'Not a valid number.')
        # usage: damage n hp
        # damages entity with index n hp points
        elif (commandstring[0] == commands[2] or commandstring[0] == shortcuts[2]) and len(commandstring) == 3:
            try:
                command = DamageCommand(self.queue, int(commandstring[1])-1, int(commandstring[2]))
            except ValueError:
                messagebox.showwarning("Run", 'Not a valid number.')
        # usage: remove n
        # remove entity with number n from queue
        elif (commandstring[0] == commands[3] or commandstring[0] == shortcuts[3]) and len(commandstring) == 2:
            try:
                command = RemoveCommand(self.queue, int(commandstring[1])-1)
            except ValueError:
                messagebox.showwarning("Run", 'Not a valid number.')
        # usage: restore n
        # revive a previously removed entity from the queue
        elif (commandstring[0] == commands[4] or commandstring[0] == shortcuts[4]) and len(commandstring) == 2:
            try:
                command = RestoreCommand(self.queue, int(commandstring[1])-1)
            except ValueError:
                messagebox.showwarning("Run", 'Not a valid number.')
        # usage: delay n up/down
        # delay entity with number n up or down
        elif (commandstring[0] == commands[5] or commandstring[0] == shortcuts[5]) and len(commandstring) == 3:
            try:
                if commandstring[2]=='down':
                    down=True
                elif commandstring[2]=='up':
                    down=False
                else:
                    messagebox.showwarning("Run","Use Up/Down")
                    return
                command = DelayCommand(self.queue, int(commandstring[1])-1,down)
            except ValueError:
                messagebox.showwarning("Run", 'Not a valid number.')
        # help
        elif (commandstring[0] == commands[6] or commandstring[0] == shortcuts[6]) and len(commandstring) == 1:
            s = helpdict['help'] + '\nCommands:\n'
            for i in commands:
                s += i + '\n'
            messagebox.showinfo("Help", s)
            return
        elif (commandstring[0] == commands[6] or commandstring[0] == shortcuts[6]) and len(commandstring) == 2:
            try:
                messagebox.showinfo("Help", helpdict[commandstring[1]])
            except KeyError:
                s = 'Not a command\nCommands:\n'
                for i in commands:
                    s += i + '\n'
                messagebox.showinfo("Help", s)
        # stop
        elif (commandstring[0] == commands[7] or commandstring[0] == shortcuts[7]) and len(commandstring) == 1:
            self.exitCallback()
        else:
            messagebox.showwarning("Run", 'Unknown Command or Wrong Syntax. Use help command for, you know, help.')

        # execute command
        if command is not None:
            try:
                self.executeCommand(command)
                self.textcommandhistory.append(self.commandstring.get())
                self.commandstring.set('')
            except IndexError:
                messagebox.showwarning("Run", "Index Out of Range.")

            # check if there are any enemies left
            if self.queue.activeEnemies() == 0 and self.started:
                messagebox.showinfo("Run", 'All enemies defeated.')

    def undoCallback(self, event=None):
        if self.started:
            self.commandhistory.undo()
            self.checkCommandHistory()
            self.refreshDisplay()

    def redoCallback(self, event=None):
        if self.started:
            self.commandhistory.redo()
            self.checkCommandHistory()
            self.refreshDisplay()

    def checkCommandHistory(self):
        # disable undo if at begin of commandhistory
        if self.commandhistory.atBegin():
            self.undoButton['state'] = 'disabled'
        else:
            self.undoButton['state'] = 'normal'
        # disable redo if at end of commandhistory
        if self.commandhistory.atEnd():
            self.redoButton['state'] = 'disabled'
        else:
            self.redoButton['state'] = 'normal'

    # refresh display of entityqueue
    def refreshDisplay(self):
        self.eqf.refresh()

    # clear display of entityqueue
    def clearDisplay(self):
        self.eqf.clear()

    def clearCallback(self):
        self.queue.clear()
        self.commandhistory.clear()
        self.names.clear()
        self.clearDisplay()
        for e in self.entities:
            e.destroy()
        self.entities = []
        self.started = False
        self.disableWidgetsOnStop()

    def executeCommand(self,command):
        command.execute()
        self.refreshDisplay()
        self.commandhistory.append(command)
        self.checkCommandHistory()

    # Menu Callbacks

    def loadEntityCallback(self):
        filenames = filedialog.askopenfilenames(initialdir=self.settings['entitydir'])
        for filename in filenames:
            try:
                f = open(filename, 'r')
                d = json.load(f)
                f.close()
                e = self.addCallback()
                e.fillIn(d)
            except OSError:
                messagebox.showerror('Load Entity', 'Could not open file ' + filename)
                e.destroyCallback()
            except (KeyError, TypeError):
                messagebox.showerror('Load Entity', 'File ' + filename + ' not in correct format')
                e.destroyCallback()

    def saveEntityCallback(self, e):
        if e.name.get() == "":
            messagebox.showwarning("Save", "No name given.")
            return
        try:
            filename = os.path.join(self.settings['entitydir'], e.name.get() + ".json")
            f = open(filename, 'w')
            d = e.toJson()
            d['amount'] = 1
            json.dump(d, f)
            f.close()
            messagebox.showinfo("Save", "Entity saved as " + filename)
        except OSError:
            messagebox.showerror("Save", "Could not save file")

    def loadPlayersCallback(self):
        for p in self.settings['playerfiles']:
            try:
                f = open(p, 'r')
                d = json.load(f)
                f.close()
                e = self.addCallback()
                e.fillIn(d)
            except OSError:
                messagebox.showerror('Load Player', 'Could not open file ' + p)
            except (KeyError, TypeError):
                messagebox.showerror('Load Player', 'File ' + p + ' not in correct format')

    def saveFightCallback(self,event=None):
        if self.started:
            filename = filedialog.asksaveasfilename(initialdir=self.settings['fightdir'], defaultextension=".json")
            if filename:
                try:
                    d = dict()
                    d["position"] = self.queue.position
                    d["round"] = self.queue.round
                    # iterate over entities in EntityQueue and save their dictionary representation to a list
                    entitiesList = []
                    for e in self.queue.queue:
                        entitiesList.append(e.__dict__)
                    d["queue"] = entitiesList
                    # iterate over EntityFrames and save their dictionary representation to a list
                    entityFramesList = []
                    for ef in self.entities:
                        entityFramesList.append(ef.toJson())
                    d["frames"] = entityFramesList
                    d["names"] = self.names
                    f = open(filename, 'w')
                    json.dump(d, f)
                    f.close()
                    messagebox.showinfo("Save Fight", "Fight saved as " + filename)
                except OSError:
                    messagebox.showerror("Save Fight", "Could not save file")

    def loadFightCallback(self, event=None):
        if self.started:
            if not messagebox.askyesno("Start", "Are you sure you  want to restart combat? Progress will be lost."):
                return
        filename = filedialog.askopenfilename(initialdir=self.settings['fightdir'])
        if filename:
            try:
                f = open(filename, 'r')
                d = json.load(f)
                f.close()
                self.queue.clear()
                self.queue.position = d["position"]
                self.queue.round = d["round"]
                for e in d["queue"]:
                    self.queue.append(Entity.fromDict(e))
                #self.queue.sort()
                self.refreshDisplay()
                for ef in d["frames"]:
                    e = self.addCallback()
                    e.fillIn(ef)
                self.names = d["names"]
                self.started = True
                self.enableWidgetsOnStart()
            except OSError:
                messagebox.showerror('Load Fight', 'Could not open file ' + filename)
            except (KeyError, TypeError):
                messagebox.showerror('Load Fight', 'File ' + filename + ' not in correct format')

    def settingsCallback(self):
        sd = SettingsDialog(self, self.settings)
        print(sd.settings)
        if sd.settings is not None:
            self.settings = sd.settings
            try:
                f = open('settings.json', 'w')
                json.dump(self.settings, f)
                f.close()
            except OSError:
                messagebox.showerror("Save Settings", "Could not save settings")

    def focusCallback(self,event=None):
        self.commandEntry.focus()

    def exitCallback(self, event=None):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()



