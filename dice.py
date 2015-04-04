#helper functions concerning dice

import random
import re
pattern=re.compile("([0-9]*)d([0-9]+)((\+|\-)[0-9]*)?")

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

def parseDice(string):
    pattern.split(string)
    


