# module that implements the command pattern for initiative(gui),
# a commandhistory array and commands

commands = ['next', 'heal', 'damage', 'remove', 'restore', 'delay', 'help', 'stop']
usage = ['', 'n hp', 'n hp', 'n', 'n', 'n up/down', 'command', '']
shortcuts = ['n', 'he', 'da', 'rem', 'res', 'de', 'h', 's']


class Command:
    def __init__(self, entityqueue):
        self.entityqueue = entityqueue

    def execute(self):
        pass

    def undo(self):
        pass


class NextCommand(Command):
    def __init__(self, entityqueue):
        Command.__init__(self, entityqueue)
        self.prevpos = 0
        self.prevround = 0

    def execute(self):
        self.prevpos = self.entityqueue.position
        self.prevround = self.entityqueue.round
        self.entityqueue.incr()

    def undo(self):
        self.entityqueue.position = self.prevpos
        self.entityqueue.round = self.prevround


class HealCommand(Command):
    def __init__(self, entityqueue, pos, hp):
        Command.__init__(self, entityqueue)
        self.pos = pos
        self.hp = hp

    def execute(self):
        self.entityqueue.heal(self.pos, self.hp)

    def undo(self):
        self.entityqueue.damage(self.pos, self.hp)


class DamageCommand(Command):
    def __init__(self, entityqueue, pos, hp):
        Command.__init__(self, entityqueue)
        self.pos = pos
        self.hp = hp

    def execute(self):
        self.entityqueue.damage(self.pos, self.hp)

    def undo(self):
        self.entityqueue.heal(self.pos, self.hp)


class RemoveCommand(Command):
    def __init__(self, entityqueue, pos):
        Command.__init__(self, entityqueue)
        self.pos = pos
        self.prevactive = False

    def execute(self):
        self.prevactive = self.entityqueue.get(self.pos).active
        self.entityqueue.withdraw(self.pos)

    def undo(self):
        self.entityqueue.get(self.pos).active = self.prevactive


class RestoreCommand(Command):
    def __init__(self, entityqueue, pos):
        Command.__init__(self, entityqueue)
        self.pos = pos
        self.prevactive = False

    def execute(self):
        self.prevactive = self.entityqueue.get(self.pos).active
        self.entityqueue.restore(self.pos)

    def undo(self):
        self.entityqueue.get(self.pos).active = self.prevactive


class DelayCommand(Command):
    def __init__(self, entityqueue, pos, down):
        Command.__init__(self, entityqueue)
        self.pos = pos
        self.down = down
        self.newpos = pos + 1 if down else pos - 1

    def execute(self):
        self.entityqueue.delay(self.pos, self.down)

    def undo(self):
        self.entityqueue.delay(self.newpos, not self.down)


class AddCommand(Command):
    def __init__(self, entityqueue, entities):
        Command.__init__(self, entityqueue)
        self.entities = entities

    def execute(self):
        for e in self.entities:
            self.entityqueue.append(e)

    def undo(self):
        for e in self.entities:
            self.entityqueue.remove(e)


class CommandHistory:
    def __init__(self):
        self.history = []
        self.position = -1

    def append(self, command):
        self.position += 1
        if self.position != len(self.history):
            self.history[self.position:] = []
        self.history.append(command)
        # print("{}/{}".format(self.position,len(self.history)))

    def undo(self):
        if self.position >= 0:
            self.history[self.position].undo()
            self.position -= 1
            # print("{}/{}".format(self.position,len(self.history)))

    def redo(self):
        if self.position + 1 < len(self.history):
            self.position += 1
            self.history[self.position].execute()
            # print("{}/{}".format(self.position,len(self.history)))

    def clear(self):
        self.history = []
        self.position = -1

    def atBegin(self):
        return self.position == -1

    def atEnd(self):
        return self.position + 1 == len(self.history)
