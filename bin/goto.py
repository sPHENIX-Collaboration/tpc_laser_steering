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
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varAllCommands as ALL_COMM
from variableDictionaryXCD2 import varTuning as TUNE

# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase

#tuning settings
'''
this is now in the variableDictionary
varTuning={
#min_distance (minimum amount we can move without doing a backoff-and-recover),
#move_tolerance (how far from destination we are allowed to be without marking it FAIL)
'Phi':[0.1,0.001],
'ThetaS':[0.00001,0.001],
'ThetaL':[0.02,0.001],
'Attenuator':[0.001,0.001],
'Dogleg':[0.01,0.001]
}
'''
    
min_distance=0.1 #in rotations
move_tolerance=0.001 #in rotations.  causes an error if it did not get this close in the final move.
sleeptime=0.2 #in seconds
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
    
def find_comm_and_set_tuning(axisName):
    #return a command lookup table matching the axis.
    #also let us know if the axis is a dogleg, so we know how to behave.
    isDogleg=False
    COMM={}
    axisType=None
    if bool(re.match(r'^.+_DL\d_A\d$',axisName)):
        axisType='Dogleg'
        isDogleg=True
    elif bool(re.match(r'^.+_TH_S$',axisName)):
        axisType='ThetaS'
    elif bool(re.match(r'^.+_TH_L$',axisName)):
        axisType='ThetaL'
    elif bool(re.match(r'^.+_PH$',axisName)):
        axisType='Phi'    
    elif bool(re.match(r'^.+_AT$',axisName)):
        axisType='Attenuator'
    else:
        print("no match of '%s' to axis types.  Critical failure!"%(axisName))
        sys.exit()
    COMM=ALL_COMM[axisType]
    global min_distance, move_tolerance
    min_distance=TUNE[axisType][0]
    move_tolerance=TUNE[axisType][1]
    #if debug:
    print("Setting COMM. channel is type %s, min_distance=%s, move_tolerance=%s"%(axisType,min_distance,move_tolerance))
    return isDogleg, COMM


def set_tuning( axisType ):
    '''
    this is now in the variableDictionary
    #tuning settings

    varTuning={
    #min_distance (minimum amount we can move without doing a backoff-and-recover),
    #move_tolerance (how far from destination we are allowed to be without marking it FAIL)
    'Phi':[0.1,0.001],
    'ThetaS':[0.00001,0.001],
    'ThetaL':[0.0001,0.001],
    'Attenuator':[0.001,0.001],
    'Dogleg':[0.01,0.001]
    }
    '''
    min_distance=TUNE[axisType][0]
    move_tolerance=TUNE[axisType][1]

    return min_distance, move_tolerance



def gotoVettedQuiet(destination,COMM,OLBool):
    #the vetting occurs in goto, so this should not be called 'bare'.
    #axisName is a real axis, destination is a float, COMM is set correctly
    #the portfile and axis is also set correctly
    destination=float(destination)

    #check if controller is busy.  If so, exit with explanation
    if debug:
        print("gotoVQ:  Check status:")
    status=readback(ADDR['STATUS'])
    position=readback(ADDR['FPOS'])

    if status!=0:
        print("NOT EXECUTED. Controller status is not 0. status: %s (%s)"%(status,_reverseLookup(STAT,status)))
        return False, position
    
    #load in our bounds as currently understood on the controller
    lb=float(readback(ADDR['HARD_STOP1']))
    hb=float(readback(ADDR['HARD_STOP2']))

    #do one final massage of our position:  If it is >hb, reduce it by 1.0 until it is not
    if COMM!=ALL_COMM["Dogleg"]: #dogleg does not get adjusted (not that we use it here in general)
        while destination >hb:
            destination=destination-1
        while destination <lb: #ditto if it is below lowbound.
            destination=destination+1
        if destination >hb: #if that correction leaves us above the hb again, it is unreachable by defined bounds.
            print("NOT EXECUTED. Controller requires %s<dest<%s, and that is not possible for any +N rotations of dest=%s"%(lb,hb,destination))
            return False, position
        
    #if we are within move tolerance of our destination, dont' move.
    if abs(destination-position)<move_tolerance:
        print("gotoVQ: dest=%s, pos=%s, abs(dest-pos)=%s<%s.  No motion necessary."%(destination, position,abs(destination-position),move_tolerance))
        return True, position
    
    #if using openloop goto, no need to jog back and forth
    #if using regular goto (using closedloop move), jogging may be necessary
    if OLBool:
        print("gotoVQ: sending command %s (%s) destination:%s"%(COMM['OPENLOOP'],'OPENLOOP',destination))
        commandSent=sendcommand(COMM['OPENLOOP'],destination) # this sleeps until it sees the status change from new_command
    else:
        #look at our position.  if we are too close, we may not move at all, so move away before going toward.
        if abs(destination-position)<min_distance:
            print("gotoVettedQuiet: destination:%s is too close to position %s.  Attempting to jog"%(destination,position))
            #try to move in the direction away from the actual destination
            jogdir=-1
            if (destination<position):
                jogdir=1
            jogtarget1=position+jogdir*2*min_distance
            jogtarget2=position-jogdir*3*min_distance

            #move away from our target first:
            if (jogtarget1>lb and jogtarget1<hb):
                gotoVettedQuiet(jogtarget1,COMM,OLBool)
            #if that doesn't work, overshoot the target instead
            elif (jogtarget2>lb and jogtarget2<hb):
                gotoVettedQuiet(jogtarget2,COMM,OLBool)
            #if neither work, admit our failure and do our best:
            else:
                print("gotoVettedQuiet: Original dest %s was too close to fpos %s, so tried to jog to %s or %s, but both are out of bounds (lb:%s, hb:%s)"%(destination,position,jogtarget1,jogtarget2,lb,hb))
            
    
        print("gotoVQ: sending command %s (%s) destination:%s"%(COMM['GOTO'],'GOTO',destination))
        commandSent=sendcommand(COMM['GOTO'],destination) # this sleeps until it sees the status change from new_command
    
    # check that goto command was sent
    if not commandSent:
        return False, readback(ADDR['FPOS'])
    
    #monitor the controller position and report at intervals of sleeptime
    position=readback(ADDR['FPOS'])
    if debug:
        print("gotoVQ:  Check position: %s"%position);
    status=readback(ADDR['STATUS'])
    if debug:
        print("gotoVQ:  Check status: %s"%status);
    #status=STAT['BUSY']
    axis=readback(ADDR['XAXIS'])
    hardstop1=readback(ADDR['HARD_STOP1'])
    hardstop2=readback(ADDR['HARD_STOP2'])
    t1=time.time()
    while status==STAT['BUSY']  and (time.time()-t1) < timeout:
        turns=readback(ADDR['TURNS'])
        position=readback(ADDR['FPOS'])
        oldposition=position
        position=readback(ADDR['FPOS'])
        turns=readback(ADDR['TURNS'])
        home=readback(ADDR['HOME'])
        print("position:%s status:%s (%s) turns:%s home:%s (not live: ax: %s lb:%1.4f hb:%1.4f) (gotoVQ)"%(position,status,_reverseLookup(STAT,status),turns,home,axis,hardstop1,hardstop2))

        #print("position:", position," (axis",axis,") status:",status," (",_reverseLookup(STAT,status),") turns:",turns)
 
        # sleep a little, and if same position, enter timeout loop
        time.sleep(sleeptime)

        # check 
        if abs(readback(ADDR['FPOS'])-position) > 3*readback('ENR'):
            t1 = time.time()

        # otherwise update status and continue
        status=readback(ADDR['STATUS']) 
        if debug:
            print ("gotoVQ: loop: check status: %s"%status)
 
    if status==STAT['BUSY']:
        writeXCD2([ADDR['STATUS'], 80]) # we need to get writeXXCD2 out of here.  maybe setStatus?
        time.sleep(sleeptime)

    #loop until controller busy flag is cleared

    #report final position and success
    if debug:
        print ("gotoVettedQuiet: finishing up.  check status and readback.")
    return True, readback(ADDR['FPOS'])

        
def goto( axisName=None, destination=None, OLBool=False):
    if axisName==None or destination==None:
        print("wrong args for goto.  requires two arguments.")
        return False, 0
    
    #check if that axis is connected.  Fail if not


    # success, targetPort, targetAxis = changeAxis( axisName )


    # change axis does the following
    # 1) checks if targetIDstr (i.e. axisName) is in ID_dict.keys()
    # 2) looks up axisName in kfDatabase
    # 3) if ret[0]/success is False, print axis not found and return False
    # 4) extracts target port and axis from ret (same as value[0], value[1])
    # 5) check if portfile exists, and if so, write target port from kfdb
    # 6) readback current XAXIS
    # 7) if XAXIS same values remain from last use and return
    # 8) otherwise create lookup table from ID_dict and find ID corresponding to current axis
    # 9) write values from current axis to file
    # 10) read from file values corresponding to current axis
    # 11) print report of what changed

    # changeAxis needs to do the following
    # 1) 


    # goto does the following
    # 1) verifies if given an axisName and destination

    # 2) looks up axisName in kfDatabase
    # 3) if not success, then print kfDatabase failed and return
    # 4) otherwise extracts target port and axis

    # 5) find command type and tuning parameters 
    # 6) check if destination is a number
    # 7) if not a number, open database of known positions and search
    # 8) check if dogleg - if so gotoDogleg instead

    # 9) write target port to portfile, target axis to XAXIS

    # 10) call gotoVQ to handle movement

    # success, value=kfDatabase.readVar(portsDb,axisName)
    # if not success:
    #     print("goto: kfDatabase failed.  Axis '%s' not connected. (or port database is stale)" % axisName)
    #     return False 
    # targetPort,targetAxis=value[0],value[1]

    didAxisChange = changeAxis( axisName )
    if not didAxisChange:
        return False, 0
    
    #set command lookup table to match the axis
    isDogleg,COMM=find_comm_and_set_tuning(axisName)
    
    #check to see if the target is a number.
    #if number: make it a float.
    if (is_number(destination)):
        targetPos=float(destination) # we handle the dogleg condition below.
            
    #if not number: open the dictionary and see if that axis has that variable set.  Fail if not
    else:
        #if we have specified a full path, go with it.
        if "/" in destination:
            keyName=destination
        else:#otherwise, assume it's from the current axis
            keyName=axisName+"/"+str(destination)
        #  get the value from the dict.
        if debug:
            print("goto: looking for value %s"%keyName)
        success,value=kfDatabase.readVar(mainDb, keyName)
        if not success:
            print("goto: kfDatabase failed.  destination '%s' not found for %s. (kfdb=%s, key=%s)" % (destination,axisName,mainDb,keyName))
            return False, 0
        #  check to see if the dict value is a number.
        #  if number: make it a float.
        if (is_number(value)):
            targetPos=float(value)
        else:
            print("goto: kfDatabase key '%s' has non-numeric value %s" % (keyName,str(value)))
            return False, 0

    #refuse to move if we are asking a dogleg to move to a numeric position (to prevent accidents)
    if isDogleg and is_number(destination):
        print("goto: refused.  To prevent breaking alignment by accident, you must use gotoDogleg, not goto, to move '%s' to '%s'."%(axisName,destination))
        return False, 0
    
    #now we are guaranteed we have a reachable axis, and a target position as a float.
    #we are also guaranteed that we are not moving a dogleg to a numeric position.

    # # set the current port through the file:
    # with open(PORTFILE,'w') as file:
    #     file.write(targetPort)
    # # changeAxis:
    # # this really needs to be 'change axis'.
    # writeXCD2([ADDR['XAXIS'],targetAxis])

    #now that we have set up the environment, we can run the 'vetted' goto:
    #this does not have a return value.  errors must be inferred from readback.
    ret=gotoVettedQuiet(targetPos,COMM,OLBool)
    if (ret[0]==False): #we didn't get where we need to go because of communication failures.
        return ret

    status=readback(ADDR['STATUS'])
    position=readback(ADDR['FPOS'])
    axis=readback(ADDR['XAXIS'])
    turns=readback(ADDR['TURNS'])
    lb=readback(ADDR['HARD_STOP1'])
    hb=readback(ADDR['HARD_STOP2'])

    residual=targetPos-position
    if COMM!=ALL_COMM["Dogleg"]: #dogleg does not get adjusted (not that we use it here in general)
        while residual >1:
            residual=residual-1
        while residual <-1: #ditto if it is below lowbound.
            residual=residual+1
        if residual >1: #if that correction leaves us above the hb again, it is unreachable by defined bounds.
            print("PANIC.  Residual is a number not between -1 and +1 after execution and reduction. Residual=%s"%(residual))
            sys.exit()

    if status==STAT['READY']:
        if abs(residual)<move_tolerance:
            print("SUCCESS. goto %s %s complete. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f"%(axisName, destination, status,_reverseLookup(STAT,status),position,axis, turns,lb,hb))
            return True, position
        elif abs(residual-math.floor(residual))<move_tolerance:
            print("SUCCESS. goto %s %s complete. status: %s (%s) position:%1.6f (with wrap-around) axis:%s turns:%s lb:%1.5f hb:%1.5f"%(axisName, destination, status,_reverseLookup(STAT,status),position,axis, turns,lb,hb))
            return True, position
        else:
            print("FAIL. goto %s %s failed in .py tolerance check: position more than %s from %s, even with wrap-arounds. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f" \
                  %(axisName,destination,move_tolerance,targetPos, status,_reverseLookup(STAT,status),position,axis, turns,lb,hb))
            return False, position
    else:
        print("FAIL. goto %s %s failed in controller. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f"%(axisName, destination, status,_reverseLookup(STAT,status),position,axis, turns,lb,hb))
        return False, position
    return False, "GOTO: PANIC!  YOU SHOULD NOT BE ABLE TO REACH HERE"



if __name__ == "__main__":
    #check args
    if len(sys.argv)==3:
        #assume first arg is leg, assume second arg is destination.
        #get its port from the db
        axis=sys.argv[1]
        dest=sys.argv[2]
        openloop=False
    elif len(sys.argv)==4:
        if sys.argv[3] != "ol":
            print("NOT EXECUTED. Incorrect final argument.  Correct usage of open loop call is:")
            print("   ./goto.py laser_name position ol")
            sys.exit()
        axis=sys.argv[1]
        dest=sys.argv[2]
        openloop=True
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("   ./goto.py laser_name position (ol)")
        sys.exit()
    #if wrong arguments, exit with explanation

    goto(axis,dest,openloop)
