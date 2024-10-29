#!/usr/bin/python3

import sys
import os
from quickAssign import writeXCD2
from quickReport import readback, reportXCD2
from updateLaserFiles import writeToFile, readFromFile
from xcdSerial import getCurrentPort
from variableDictionaryXCD2 import varDict
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varDoglegCommands as COMM
from variableDictionaryXCD2 import varUniqueID as AXID

# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase


# tuning settings
sleeptime=0.5 #in seconds
debug=False
portsDb="xcd2_ports.kfdb"
PORTFILE="XCD_current_port"


def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print(f"gotoDogleg lookup failed.  KeyError: {e}")
        sys.exit()
    return key  



def changeAxis( targetIDstr ):
    #check if controller is busy.  If so, exit with explanation
    if debug:
        print("changeAxis:  Check status:")

    # commenting out the status check, which causes failures if something is unplugged -- we're unable to switch away.
    # print("before readback")
#    status=readback(ADDR['STATUS'])
#    print("after readback")
#    
#    if status!=0:
#        if status == 98.0:
#            print("Axis must be set by calling setAxis.py")
#        else:
#            print("NOT EXECUTED. Controller status is not 0.")
#            sys.exit()
#
#    print('about to look in AXID keys')

    # check if axis we want to change to is a valid motor, and if not exit
    if targetIDstr not in AXID.keys():
        print("changeAxis: Axis ID '%s' not recognized. Axis ID list given as:"%targetIDstr)
        print(AXID.keys())
        return False

    # now find port corresponding to new axis 
    # first open port database file
    # print("about to query db")
    success, dbResponse = kfDatabase.readVar(portsDb, targetIDstr)

    # exit if we don't have a port
    if not success:
        print("changeAxis: Axis ID '%s' not found in database '%s'.  Run updatePorts.py." % (targetIDstr, portsDb))
        return False
    
    # otherwise print the port and axis returned
    print("kfDatabase returns %s" % dbResponse)

    # extract port and axis from the database return value
    targetPort = dbResponse[0]
    targetAxis = dbResponse[1]


    # (this will change to object in class when we refactor)
    if not (os.path.exists(PORTFILE)):
        print("changeAxis: PORTFILE %s does not exist.  PANIC" % PORTFILE)
        return False

    # pull old port from PORTFILE
    with open(PORTFILE, 'r') as file:
        oldPort = file.readline()
    
    # before we go, if the current port exists, save the old FPOS and nturns, just in case:
    oldPortExists=False
    oldID=-1
    oldAxis=-1
    oldStatus=-1
    oldPos=-1000
    oldTurns=-1000
    if os.path.exists(oldPort):
        oldPortExists=True
        oldID=readback(ADDR['ID'])
        oldAxis=readback(ADDR['XAXIS'])
        oldStatus=readback(ADDR['STATUS'])
        oldPos=readback(ADDR['FPOS'])
        oldTurns=readback(ADDR['TURNS'])


    # write all variables to file corresponding to old ID before switching ports
    if oldPortExists:
        oldIDstr = _reverseLookup(AXID, oldID)
        writeToFile('laserConfigs/' +  oldIDstr )
    
    # set active port
    with open(PORTFILE, 'w') as file:
        file.write(targetPort)

    
    # readback current axis to compare with target axis
    currentAxis = readback(ADDR['XAXIS'])
    # check if current ID and target ID are the same, or if the correct port's axis is the same as our target
    currentID = readback(ADDR['ID'])
    currentIDstr = _reverseLookup(AXID, currentID)
    
    if (currentAxis == targetAxis):
        if (oldPortExists and oldPort==targetPort):
            print("changeAxis: XAXIS and Port are unchanged. (target:%s. %s says this is %s, axis %s) Values remain from last use, not loaded from file."%(targetIDstr,portsDb,targetPort,targetAxis))
            print("remains: %s port=%s, pos=%s, axis=%s, stat=%s, turns=%s"%(_reverseLookup(AXID, oldID),oldPort,oldPos,oldAxis,oldStatus,oldTurns))
            return True
        else:
            print("changeAxis: Port changed from %s . XAXIS is already set correctly on %s. (target:%s. %s says this is %s, axis %s) Values remain from last use, not loaded from file."%(oldPort,targetIDstr,targetPort,portsDb,targetPort,targetAxis))
            currentPos=readback(ADDR['FPOS'])
            currentStatus=readback(ADDR['STATUS'])
            currentTurns=readback(ADDR['TURNS'])
            if (oldPortExists):
                print("was: %s(%s) port=%s, pos=%s, axis=%s, stat=%s, turns=%s"%(_reverseLookup(AXID, oldID),oldID,oldPort,oldPos,oldAxis,oldStatus,oldTurns))
            else:
                print("was: invalid port %s"%oldPort)
            print("now: %s(%s) port=%s, pos=%s, axis=%s, stat=%s, turns=%s"%(currentIDstr,currentID,targetPort,currentPos,currentAxis,currentStatus,currentTurns))
            writeXCD2([ADDR['STATUS'], 0])
            return True
    #if the axis on the desired port is already what we desire, there is no need to load new info.  This needs more discussion.

    # find file corresponding to target ID and load from it
    readBool = readFromFile('laserConfigs/' + targetIDstr )

    # now read the current state:
    newAxis=readback(ADDR['XAXIS'])
    newPos=readback(ADDR['FPOS'])
    if (newAxis!=targetAxis): #possibly port file is corrupted, but in any case we still have a change to make:
        writeXCD2([ADDR['XAXIS'], targetAxis])
        writeXCD2([ADDR['FPOS'], newPos])
        newAxis=readback(ADDR['XAXIS'])
    newID=readback(ADDR['ID'])
    newStatus=readback(ADDR['STATUS'])
    writeXCD2([ADDR['STATUS'], 0])
    newTurns=readback(ADDR['TURNS'])
        
        

    if readBool:
        print("changeAxis: Axis changed to '%s' on port '%s'"% (targetIDstr, targetPort))
    else:
        print("FAILURE: changeAxis: Axis could not be changed to '%s' on port '%s' - variables not read from file."% (targetIDstr, targetPort))
    print("was: %s(%s) port=%s, axis=%s, pos=%s, stat=%s, turns=%s"%(_reverseLookup(AXID, oldID),oldID,oldPort,oldAxis,oldPos,oldStatus,oldTurns)) 
    print("now: %s(%s) port=%s, axis=%s, pos=%s, stat=%s, turns=%s"%(_reverseLookup(AXID, newID),newID,targetPort,newAxis,newPos,newStatus,newTurns)) 
    
    return readBool  


if __name__ == "__main__":
    # check args
    # if wrong arguments, exit with explanation
    if len(sys.argv) == 2: # sys.argv has arg 1 as the command itself
        changeAxis(sys.argv[1])
    elif len(sys.argv)==3 and sys.argv[2]==1:
        debug=True
        changeAxis(sys.argv[1])
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("   ./changeAxisDogleg.py L#_DL#_A#")
        print("or turn on debug with   ./changeAxisDogleg.py L#_DL#_A# 1")
        sys.exit()



# success, targetPort, targetAxis = changeAxis( axisName )


# change axis does the following
# 1) checks if targetIDstr (i.e. axisName) is in ID_dict.keys()
# 2) looks up axisName in kfDatabase
# 3) if ret[0]/success is False, print axis not found
# 4) extracts target port and axis from ret (same as value[0], value[1])
# 5) check if portfile exists, and if so, write target port from kfdb
# 6) readback current XAXIS
# 7) if XAXIS same values remain from last use and return
# 8) otherwise create lookup table from ID_dict and find ID corresponding to current axis
# 9) write values from current axis to file
# 10) read from file values corresponding to current axis
# 11) print report of what changed
