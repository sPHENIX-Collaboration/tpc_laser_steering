#!/usr/bin/python3

import sys
import os
from quickReport import readback
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varUniqueID as AXID


# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase
mainDb="axis_parameters.kfdb"


def savePosition(keyName,newness):
    position = readback(ADDR['FPOS'])
    ret=kfDatabase.writeVar(mainDb,keyName,position,newness)
    if not ret:
        print("failed to save %s to %s as %s.  Might need 'new', or might already have that value?"%(position,mainDb,keyName))
    else:    
        print("saved %s to %s as %s"%(position,mainDb,keyName))


if __name__ == "__main__":
    debug=True

    #check args
    referenceEgg=None
    if len(sys.argv)<2 or len(sys.argv)>3: 
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is ./savePosition.py key or ./savePosition.py key new")
        sys.exit()
    keyName=sys.argv[1]
    newness=''
    if len(sys.argv) == 3: #note that sys.argv has arg 1 as the command itself
        newness='new'
    #if wrong arguments, exit with explanation
    savePosition(keyName,newness)
