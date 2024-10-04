#!/usr/bin/python3

from quickAssign import sendcommand, writeXCD2
from quickReport import readback
from changeAxisDogleg import changeAxis
import sys
import time
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varAttenuatorCommands as COMM
from homePhi import homePhi
from homeThetaL import homeThetaL
from homeThetaS import homeThetaS



# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase


#tuning settings
sleeptime = 0.5 # in seconds
timeout = 10    # in seconds
debug=False
mainDb="axis_parameters.kfdb"
matchTolerance=0.001


def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print("reverse lookup failed.  KeyError: %s"%(e))
        sys.exit()
    return key


#homeAttenuator() should return success, lowbound, highbound,home, in that order.

def homeEgg(laser, referenceEgg):
    print("homeEgg needs to have its 'reference egg' stuff amended.  And needs to move the thL to a safe position.  Proceed with caution!")
    dbRef=["default"]*3
    laserAxisName=["default_laser"]*3
    hResult=[False]*3
    lb=[0]*3
    hb=[0]*3
    home=[0]*3
        
    dbRef[0]=referenceEgg+"_TH_L"
    dbRef[1]=referenceEgg+"_TH_S"
    dbRef[2]=referenceEgg+"_PH"
    laserAxisName[0]=laser+"_TH_L"
    laserAxisName[1]=laser+"_TH_S"
    laserAxisName[2]=laser+"_PH"
    
    cResult=changeAxis(laserAxisName[0])
    writeXCD2([ADDR['STATUS'], 0])    
    if cResult==False:
        print("Could not changeAxis(%s)."%laserAxisName[0])
        return False
    hResult[0],lb[0],hb[0],home[0]=homeThetaL(dbRef[0])
    #we should move thL to a safe position here!
    
    cResult=changeAxis(laserAxisName[1])
    writeXCD2([ADDR['STATUS'], 0])
    if cResult==False:
        print("Could not changeAxis(%s)."%laserAxisName[1])
        return False
    hResult[1],lb[1],hb[1],home[1]=homeThetaS(dbRef[1])

    cResult=changeAxis(laserAxisName[2])
    writeXCD2([ADDR['STATUS'], 0])
    if cResult==False:
        print("Could not changeAxis(%s)."%laserAxisName[2])
        return False
    hResult[2],lb[2],hb[2],home[2]=homePhi(dbRef[2])


    print("\n\nHome procedure for egg %s at %s complete:"%(referenceEgg,laser))
    for i in range(0,3):
        print("\t%s at %s: %s.  lb:%s hb:%s home:%s"%(dbRef[i],laserAxisName[i],("Success"*hResult[i]+">>FAIL<<"*(not hResult[i])),lb[i],hb[i],home[i]))
    return hResult[0] and hResult[1] and hResult[2]



    
if __name__ == "__main__":

    #check args
    referenceEgg=None
    if len(sys.argv) == 2: #note that sys.argv has arg 1 as the command itself
        laser="DEBUG"
        referenceEgg=sys.argv[1]
    elif len(sys.argv) == 3: #note that sys.argv has arg 1 as the command itself
        laser=sys.argv[1]
        referenceEgg=sys.argv[2]
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is ./homeEgg.py Egg or /homeEgg.py Laser Egg")
        sys.exit()
    homeEgg(laser,referenceEgg)
              
