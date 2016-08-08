# represents an entity in combat, player or enemy
class Entity:
    formActive = " {:15} ({:2.0f}) {:2}/{:2} "
    formInactive = "[{:15} ({:2.0f}) {:2}/{:2}]"

    # constructor
    def __init__(self, name, bonus, maxHealth, roll, ac, isPlayer=False):
        self.active = True
        self.name = name
        self.bonus = bonus
        self.maxHealth = maxHealth
        self.health = maxHealth
        self.isPlayer = isPlayer
        self.roll = roll
        self.ac=ac
        self.updateinitiative()

    def updateinitiative(self):
        if self.isPlayer:
            self.initiative = self.roll + self.bonus
        else:
            self.initiative = self.roll + self.bonus * 1.001

    # clas method for constructing using dict
    @classmethod
    def fromDict(cls, d):
        e = cls(d["name"], d["bonus"], d["maxHealth"], 0, d["ac"], d["isPlayer"])
        e.active = d["active"]
        e.health = d["health"]
        e.initiative = d["initiative"]
        return e

    def damage(self, damage):
        self.health = max(self.health - damage, 0)
        if self.health == 0:
            self.active = False

    def heal(self, heal):
        if self.health == 0 and heal > 0:
            self.active = True
        self.health = min(self.health + heal, self.maxHealth)

    def __str__(self):
        if self.active:
            return self.formActive.format(self.name, self.initiative, self.health, self.maxHealth)
        else:
            return self.formInactive.format(self.name, self.initiative, self.health, self.maxHealth)


class EntityQueue:
    arrow = "-->"
    header = (len(arrow) + 1) * ' ' + "Round {}\n\n"
    form = "{} {:2}) {}\n"

    def __init__(self):
        self.queue = []
        self.position = 0
        self.length = 0
        self.index = -1
        self.round = 0

    def get(self, pos=-1):
        if pos == -1:
            return self.queue[self.position]
        else:
            return self.queue[pos]

    def append(self, entity):
        added=False
        i=0
        while not added and i < self.length:
            if self.queue[i].initiative < entity.initiative:
                self.queue.insert(i,entity)
                added=True
            i+=1
        if not added:
            self.queue.append(entity)
        self.length += 1

    def remove(self, entity):
        try:
            self.queue.remove(entity)
            self.length -= 1
        except ValueError:
            pass

    def clear(self):
        self.queue = []
        self.position = 0
        self.length = 0
        self.index = -1
        self.round = 0

    # sorts the queue on the initiative of entities, in descending order
    def sort(self):
        self.queue.sort(key=lambda x: x.initiative, reverse=True)

    # increments the position of the active entity. Only entities that are marked active
    # are considered. Loops back to begin
    def incr(self):
        if self.length != 0:
            if not self.activeEnemies():
                return
            done = False
            while not done:
                self.position += 1
                if self.position == self.length:
                    self.position = 0
                    self.round += 1
                if self.queue[self.position].active:
                    done = True

    # returns the number of enemies currently active in the queue
    def activeEnemies(self):
        e = 0
        for entity in self.queue:
            if not entity.isPlayer and entity.active:
                e += 1
        return e

    def heal(self, pos, hp):
        self.queue[pos ].heal(hp)

    def damage(self, pos, hp):
        self.queue[pos].damage(hp)

    def withdraw(self, pos):
        self.queue[pos].active = False

    def restore(self, pos):
        self.queue[pos].active = True

    def delay(self, pos=-1,down=True):
        if pos==-1:
            pos=self.position

        if down:
            change=pos+1
        else:
            change=pos-1

        tmp=self.queue[change]
        self.queue[change]=self.queue[pos]
        self.queue[pos]=tmp

    # returns string representation of the queue
    # active entity is marked with arrow
    def __str__(self):
        s = "\n"
        s += self.header.format(self.round + 1)
        for i in range(self.length):
            s += self.form.format(self.arrow if i == self.position else " " * len(self.arrow), i + 1, self.queue[i])
        return s

    # iterator for use in for loops.
    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if self.index == self.length:
            self.index = -1
            raise StopIteration
        return self.queue[self.index]
