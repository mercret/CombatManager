#helper functions concerning dice

from enum import Enum
import random
import re
pattern1=re.compile("^([0-9]*)(d4|d6|d8|d10|d12|d20|d100)((\+|\-)[0-9]*)?$")
pattern2=re.compile("^[1-9][0-9]*$")

class Dice(Enum):
    d4=4
    d6=6
    d8=8
    d10=10
    d12=12
    d20=20
    d100=100

    def roll(self):
        if self.value==100:
            return 10*random.randrange(1,11)
        else:
            return random.randrange(1,self.value+1)

    def isRoll(self,roll):
        return roll>0 and roll<=self.value

def isRoll(string):
    return pattern1.match(string) is not None

def getRoll(string):
    if pattern1.match(string):
        spl=pattern1.split(string)[1:-2]
        if spl==[]:
            raise ValueError("Wrong syntax")
        dice=spl[1]
        if spl[0]=='':
            throws=1
        else:
            throws=int(spl[0])
        if spl[2]==None:
            mod=0
        else:
            mod=int(spl[2])
        roll=0
        for i in range(throws):
            roll+=Dice[dice].roll()
        return roll+mod

def isHealth(string):
    return pattern1.match(string) is not None or pattern2.match(string) is not None

def getHealth(string):
    if pattern1.match(string):
        return getRoll(string)
    if pattern2.match(string):
        return int(string)
        
    
    
    
    


