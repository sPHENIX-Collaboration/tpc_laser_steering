#!/usr/bin/python3

# This is designed to tell a particular named motor axis to go to a particular named position.
# To prevent alignment accidents, it will not send a dogleg to a numeric position.  for that, you need to use gotoDogleg
# If the axis is not connected, or the requested named position is not in the database, it fails.

from quickAssign import sendcommand,writeXCD2
from quickReport import readback
from changeAxisDogleg import changeAxis
#from dummySerial import sendcommand,readback,changeAxis, writeXCD2
import sys
import re
import time
import math
from goto import gotoVettedQuiet, find_comm_and_set_tuning
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varAllCommands as ALL_COMM

# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase

#tuning settings
sleeptime=0.6 #in seconds
timeout=10 #in seconds
debug=False
portsDb="xcd2_ports.kfdb"
#mainDb="axis_parameters.kfdb"
#portsDb="test_only_xcd2_ports.kfdb"
mainDb="axis_parameters.kfdb"
PORTFILE="XCD_current_port"

#{later:
#get current rotations
#calculate destination nRotations
#if that's tolerable
#}



def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print(f"_reverseLookup failed.  KeyError: {e}")
        sys.exit()
    return key  

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
 
def gotoRelative( axisName=None, destination=None):
    if axisName==None or destination==None:
        print("wrong args for goto.  requires two arguments.")
        return False
    
    #check if that axis is connected.  Fail if not
    success, value=kfDatabase.readVar(portsDb,axisName)
    if not success:
        print("goto: kfDatabase failed.  Axis '%s' not connected. (or port database is stale)" % axisName)
        return False
    targetPort,targetAxis=value[0],value[1]
    
    #set command lookup table to match the axis
    isDogleg,COMM=find_comm_and_set_tuning(axisName)
    
    #check to see if the target is a number.
    #if number: make it a float.
    if (is_number(destination)):
        relativePos=float(destination) # we handle the dogleg condition below.
    else:
        print("gotoRelative can not go to named positions.  use goto")
        return False

    #refuse to move if we are asking a dogleg to move to a numeric position (to prevent accidents)
    if isDogleg:
        print("gotoRelative: refused.  To prevent breaking alignment by accident, you must use gotoDogleg, not goto, to move '%s' to '%s'."%(axisName,destination))
        return
    
    #now we are guaranteed we have a reachable axis, and a target position as a float.
    #we are also guaranteed that we are not moving a dogleg to a numeric position.


    
    #set the current port through the file:
    with open(PORTFILE,'w') as file:
        file.write(targetPort)
    #changeAxis:
    #this really needs to be 'change axis'.
    writeXCD2([ADDR['XAXIS'],targetAxis])


    
    #now that we have set up the environment, we need to calculate the desired position in absolute terms:
    currentPos=readback(ADDR['FPOS'])
    targetPos=currentPos+relativePos

    #now we can run the 'vetted' goto, which asumes the target position, comm, etc are all set to proper inputs
    #this does not have a return value.  errors must be inferred from readback.
    ret=gotoVettedQuiet(targetPos,COMM)
    if (ret[0]==False): #we didn't get where we need to go because of communication failures.
        return ret

    status=readback(ADDR['STATUS'])
    position=readback(ADDR['FPOS'])
    axis=readback(ADDR['XAXIS'])
    turns=readback(ADDR['TURNS'])
    lb=readback(ADDR['HARD_STOP1'])
    hb=readback(ADDR['HARD_STOP2'])

    residual=targetPos-position



    if status==STAT['READY']:
        if abs(residual)<move_tolerance:
            print("SUCCESS. gotoRelative %s %s complete. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f"%(axisName, destination, status,_reverseLookup(STAT,status),position,axis, turns,lb,hb))
            return True, position
        elif abs(residual-floor(residual))<move_tolerance:
            print("SUCCESS. gotoRelative %s %s complete. status: %s (%s) position:%1.6f (with wrap-around) axis:%s turns:%s lb:%1.5f hb:%1.5f"%(axisName, destination, status,_reverseLookup(STAT,status),position,axis, turns,lb,hb))
            return True, position
        else:
            print("FAIL. gotoRelative %s %s failed in .py tolerance check: position more than %s from %s, even with wrap-arounds. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f"%(axisName,destination,move_tolerance,targetPos, status,_reverseLookup(STAT,status),position,axis, turns,lb,hb))
            return False, position
    else:
        print("FAIL. goto %s %s failed in controller. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f"%(axisName, destination, status,_reverseLookup(STAT,status),position,axis, turns,lb,hb))
        return False, position
    return False, "GOTORELATIVE: PANIC!  YOU SHOULD NOT BE ABLE TO REACH HERE"





if __name__ == "__main__":
    #check args
    if len(sys.argv)==3:
        #assume first arg is leg, assume second arg is destination.
        #get its port from the db
        axis=sys.argv[1]
        dest=sys.argv[2]
    elif len(sys.argv)==4:
        if sys.argv[3]=='deg' or sys.argv[3]=='degree':
            #assume first arg is leg, assume second arg is destination.
            #get its port from the db
            axis=sys.argv[1]
            dest=1.0/360.0*float(sys.argv[2])
        else:
            print("don't know that unit: '%s'.  exiting."%sys.argv[3])
            sys.exit()
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("   ./gotoRelative.py laser_axis_name position")
        sys.exit()
    #if wrong arguments, exit with explanation

    gotoRelative(axis,dest)
