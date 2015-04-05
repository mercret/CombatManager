#helper functions concerning dice

import random
import re
pattern1=re.compile("^([0-9]*)d(4|6|8|10|12|20|100)((\+|\-)[0-9]*)?$")
pattern2=re.compile("^[1-9][0-9]*$")

#roll a dice between 1-max
def diceThrow(maximum):
    return random.randrange(1,maximum+1)

def d4():
    return diceThrow(4)

def d6():
    return diceThrow(6)

def d8():
    return diceThrow(8)

def d10():
    return diceThrow(10)

def d12():
    return diceThrow(12)

def d20():
    return diceThrow(20)

def d100():
    return 10*d10()

def isHealth(string):
    return pattern1.match(string)!=None or pattern2.match(string)!=None

def getHealth(string):
    if pattern1.match(string):
        spl=pattern1.split(string)[1:-2]
        if spl==[]:
            raise ValueError("Wrong syntax")
        dice=int(spl[1])
        if spl[0]=='':
            throws=1
        else:
            throws=int(spl[0])
        if spl[2]==None:
            mod=0
        else:
            mod=int(spl[2])
        health=0
        for i in range(throws):
            health+=diceThrow(dice)
        return health+mod
    if pattern2.match(string):
        return int(string)
        
    
    
    
    


