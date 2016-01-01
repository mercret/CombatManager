import initiative

#module that implements the command pattern for initiative(gui)
#and a commandhistory array

class Command:

    def __init__(self,entityqueue):
        self.entityqueue=entityqueue

    def execute(self):
        pass

    def undo(self):
        pass

class NextCommand(Command):

    def __init__(self,entityqueue):
        Command.__init__(self,entityqueue)
        self.prevpos=0
        self.prevround=0

    def execute(self):
        self.prevpos=self.entityqueue.position
        self.prevround=self.entityqueue.round
        self.entityqueue.incr()

    def undo(self):
        self.entityqueue.position=self.prevpos
        self.entityqueue.round=self.prevround

class HealCommand(Command):

    def __init__(self,entityqueue,pos,hp):
        Command.__init__(self,entityqueue)
        self.pos=pos
        self.hp=hp
        self.prevhealth=0

    def execute(self):
        self.prevhealth=self.entityqueue.get(self.pos).health
        self.entityqueue.heal(self.pos,self.hp)

    def undo(self):
        self.entityqueue.get(self.pos).health=self.prevhealth

class DamageCommand(Command):

    def __init__(self,entityqueue,pos,hp):
        Command.__init__(self,entityqueue)
        self.pos=pos
        self.hp=hp
        self.prevhealth=0

    def execute(self):
        self.prevhealth=self.entityqueue.get(self.pos).health
        self.entityqueue.damage(self.pos,self.hp)

    def undo(self):
        self.entityqueue.get(self.pos).health=self.prevhealth
    
class RemoveCommand(Command):

    def __init__(self,entityqueue,pos):
        Command.__init__(self,entityqueue)
        self.pos=pos
        self.prevactive=False

    def execute(self):
        self.prevactive=self.entityqueue.get(self.pos).active
        self.entityqueue.remove(self.pos)

    def undo(self):
        self.entityqueue.get(self.pos).active=self.prevactive

class RestoreCommand(Command):

    def __init__(self,entityqueue,pos):
        Command.__init__(self,entityqueue)
        self.pos=pos
        self.prevactive=False

    def execute(self):
        self.prevactive=self.entityqueue.get(self.pos).active
        self.entityqueue.restore(self.pos)

    def undo(self):
        self.entityqueue.get(self.pos).active=self.prevactive

class DelayCommand(Command):

    def __init__(self,entityqueue,change):
        Command.__init__(self,entityqueue)
        self.change=change
        self.entity=None
        self.previnit=0

    def execute(self):
        self.previnit=self.entityqueue.get().initiative
        self.entity=self.entityqueue.get()
        self.entityqueue.delay(self.change)

    def undo(self):
        self.entity.initiative=self.previnit
        #order may have changed
        self.entityqueue.sort()

class CommandHistory:

    def __init__(self):
        self.history=[]
        self.position=0

    def append(self,command):
        self.history.append(command)
        self.position+=1

        
