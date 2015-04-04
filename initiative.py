#!/bin/python3

import dice
import json
import sys


commands=['next','heal','damage','remove','restore','delay','help','stop']
usage=['','n hp','n hp','n','n','n','command','']
shortcuts=['n','h','da','rem','res','de','h','s']
helpform='Usage: {} {}\nShortcut: {}\n{}'
helpmessages=['Moves to next entity in the queue',
              'Heals entity with index n hp points',
              'Damages entity with index n hp points',
              'Removes entity with index n from queue, by setting it to inactive',
              'Restore entity with index n to queue, by setting it to active',
              'Delays current entity, n is substracted from initiative value. n can be negative',
              'Displays help about command',
              'Stop the program']
#[helpform.format(commands[x],usage[x],shortcuts[x],helpmessages[x]) for x in range(0,len(commands))]
helpdict=dict(zip(commands,[helpform.format(commands[x],usage[x],shortcuts[x],helpmessages[x]) for x in range(0,len(commands))]))
helpdict.update(dict(zip(shortcuts,[helpform.format(commands[x],usage[x],shortcuts[x],helpmessages[x]) for x in range(0,len(commands))])))


#asks player names, initiative bonuses and health, saves them to json format
def makePlayerFile(file='players.json'):
    done=False
    ok=False
    l=[]
    while not done:
        d=dict()
        name=input('Player Name (Enter to stop): ')
        if name=='':
            done=True
        else:
            d['name']=name
            ok=False
            while not ok:
                try:
                    bonus=input('Player Bonus: ')
                    d['bonus']=int(bonus)
                    ok=True
                except ValueError:
                    print('Not a valid number.')
            ok=False
            while not ok:
                try:                    
                    health=input('Player Health: ')
                    d['maxHealth']=int(health)
                    ok=True
                except ValueError:
                    print('Not a valid number.')            
            l.append(d)
    try:
        f=open(file,'w')
        json.dump(l,f)
        f.close()
    except OSError:
        print("Could not open file")
    

#represents an entity in combat, player or enemy
class Entity:
    formActive=" {:10} ({:2.0f}) {:2}/{:2} "
    formInactive="[{:10} ({:2.0f}) {:2}/{:2}]"
    def __init__(self,name,bonus,maxHealth,roll,isPlayer=False):
        self.active=True
        self.name=name
        self.maxHealth=maxHealth
        self.health=maxHealth
        self.isPlayer=isPlayer
        if isPlayer:
            self.initiative=roll+bonus
        else:
            self.initiative=roll+bonus*1.001
    def damage(self, damage):
        self.health=max(self.health-damage,0)
        if self.health==0:
            self.active=False
    def heal(self, heal):
        if self.health==0 and heal>0:
            self.active=True
        self.health=min(self.health+heal,self.maxHealth)
    def __str__(self):
        if self.active:
            return self.formActive.format(self.name,self.initiative,self.health,self.maxHealth)
        else:
            return self.formInactive.format(self.name,self.initiative,self.health,self.maxHealth)

class EntityQueue:
    arrow="-->"
    form="{} {:2}) {}\n"
    def __init__(self):
        self.queue=[]
        self.position=0
        self.length=0
        self.index=-1
    def append(self, entity):
        self.queue.append(entity)
        self.length+=1
    #sorts the queue on the initiative of entities, in descending order
    def sort(self):
        self.queue.sort(key=lambda x:x.initiative,reverse=True)
    #increments the position of the active entity. Only entities that are marked active
    #are considered. Loops back to begin
    def incr(self):
        if self.length!=0:
            done=False
            while not done:        
                self.position=(self.position+1)%self.length
                if self.queue[self.position].active:
                    done=True
    #returns the number of enemies currently active in the queue
    def activeEnemies(self):
        e=0
        for entity in self.queue:
            if not entity.isPlayer and entity.active:
                e+=1
        return e
    def heal(self,pos,hp):
        self.queue[pos-1].heal(hp)
    def damage(self,pos,hp):
        self.queue[pos-1].damage(hp)
    def remove(self,pos):
        self.queue[pos-1].active=False
    def restore(self,pos):
        self.queue[pos-1].active=True
    def delay(self,change):        
        self.queue[queue.position].initiative-=change
        self.sort()

    #returns string representation of the queue
    #active entity is marked with arrow
    def __str__(self):
        s="\n"
        for i in range(self.length):
            s+=self.form.format(self.arrow if i==self.position else " "*len(self.arrow),i+1,self.queue[i])
        return s
    #iterator for use in for loops. Not used currently
    def __iter__(self):
        return self
    def __next__(self):
        self.index+=1 
        if self.index==self.length:
            raise StopIteration               
        return self.queue[self.index]

#load players stored in json format from file, ask their roll, and append them to queue
#if no file is found, user will be prompted to create one
def getPlayers(queue,file='players.json'):
    formRoll='Roll for {} (Bonus={}): '
    try:
        f=open(file,'r')
        l=json.load(f)
        f.close()
        for player in l:
            #todo: ask for health
            ok=False
            while not ok:
                try:
                    roll=input(formRoll.format(player['name'],player['bonus']))
                    roll=int(roll)
                    ok=True
                except ValueError:
                    print('Not a valid number.')                    
            queue.append(Entity(player['name'],player['bonus'],player['maxHealth'],roll,True))
    except FileNotFoundError:
        create=''
        while not (create=='y' or create=='n'):
            create=input('Player file not found. Create one? (y/n): ')
        if create=='y':
            makePlayerFile(file)
            getPlayers(queue,file)
    except OSError:
        print('Could not open player file')

        
#ask for enemies, name is asked, bonus, and amount. roll is automatically generated.
#when amount>1, the name format is name 1, name 2, ...
def getEnemies(queue):
    done=False
    while not done:
        name=input('Name (Press enter to stop): ')
        if name=="":
            done=True
        else:
            ok=False
            while not ok:                
                try:
                    bonus=input('Initiative Bonus: ')
                    bonus=int(bonus)
                    ok=True
                except ValueError:
                    print('Not a valid number.')
            ok=False
            while not ok:
                try:
                    health=input('Health: ')
                    health=int(health)
                    ok=True
                except ValueError:
                    print('Not a valid number.')
            ok=False
            while not ok:
                amount=input('Amount (Enter for 1): ')                                    
                if amount=='':
                    amount=1
                    ok=True
                else:
                    try:
                        amount=int(amount)
                        ok=True
                    except ValueError:
                        print('Not a valid number.')
            if amount==1:
                queue.append(Entity(name,bonus,health,dice.d20()))
            else:
                for i in range(amount):
                    queue.append(Entity(name+" "+str(i+1),bonus,health,dice.d20()))
                                 

def run():
    queue=EntityQueue()
    print('Enemies:')
    getEnemies(queue)
    print('Players:')
    #check if a player file was given, otherwise use standard (=players.json)
    if len(sys.argv)==2:
        getPlayers(queue,sys.argv[1])
    else:
        getPlayers(queue)
    queue.sort()
    print(queue)
    done=False
    while not done:
        command=input('Command: ')
        command=command.split()
        if len(command)==0:
            pass
        #usage: next
        #make the next active entity in the queue, the acting entity
        elif (command[0]==commands[0] or command[0]==shortcuts[0]) and len(command)==1:
            queue.incr()
            print(queue)
        #usage: heal n hp
        #heals entity with index n hp points
        elif (command[0]==commands[1] or command[0]==shortcuts[1]) and len(command)==3:
            try:
                pos=int(command[1])
                heal=int(command[2])
                queue.queue[pos-1].heal(heal)
                print(queue)
            except (ValueError, IndexError):
                print('Not a valid number')
        #usage: damage n hp
        #damages entity with index n hp points
        elif (command[0]==commands[2] or command[0]==shortcuts[2]) and len(command)==3:
            try:
                pos=int(command[1])
                damage=int(command[2])
                queue.queue[pos-1].damage(damage)
                print(queue)
            except (ValueError, IndexError):
                print('Not a valid number')
        #usage: remove n
        #remove entity with number n from queue        
        elif (command[0]==commands[3] or command[0]==shortcuts[3]) and len(command)==2:
            try:
                pos=int(command[1])
                queue.queue[pos-1].active=False                
                print(queue)
            except (ValueError, IndexError):
                print('Not a valid number')
        #usage: restore n
        #revive a perviously removed entity from the queue
        elif (command[0]==commands[4] or command[0]==shortcuts[4]) and len(command)==2:
            try:
                pos=int(command[1])
                queue.queue[pos-1].active=True
                print(queue)
            except (ValueError,IndexError):
                print('Not a valid number')
        #usage: delay n
        #substract n from current entity. n can be negative.
        elif (command[0]==commands[5] or command[0]==shortcuts[5]) and len(command)==2:
            try:                
                change=int(command[1])
                queue.queue[queue.position].initiative-=change
                queue.sort()
                print(queue)
            except ValueError:
                print('Not a valid number')

        elif (command[0]==commands[6] or command[0]==shortcuts[6]) and len(command)==1:
            print(helpdict['help'])
            print('Commands:')
            for i in commands:
                print(i)
        elif(command[0]==commands[6] or command[0]==shortcuts[6]) and len(command)==2:
            try:
                print(helpdict[command[1]])
            except KeyError:
                print('Not a command')
                print('Commands:')
                for i in commands:
                    print(i)
        #usage: stop
        #stops the program
        elif (command[0]==commands[7] or command[0]==shortcuts[7]) and len(command)==1:
            done=True
        else:
            print('Unknown Command or Wrong Syntax')
        #check if there are any enemies left
        if queue.activeEnemies()==0:
            print('All enemies defeated.')
            done=True

#needed to run from command line
#usage: python3 initiative.py (player file)
#Did you expect this message about evil world conquest?
if __name__=="__main__":
    run()
