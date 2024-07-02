#! /usr/bin/python3

from quickAssign import sendcommand, writeXCD2
from quickReport import readback
import sys
import time
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varPhiCommands as COMM


# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase


#tuning settings
sleeptime=0.3 #in seconds
debug=False
mainDb="test_only_axis_parameters.kfdb"
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


def homePhi(referenceEgg=None):
    #check if controller is busy.  If so, exit with explanation
    if debug:
        print("goto:  Check status:")
    status=readback(ADDR['STATUS'])

    if status!=0:
        print("NOT EXECUTED. Controller status is not 0.")
        return False,0,0,0


    dummyHome=-1000
    writeXCD2([ADDR['HOME'],dummyHome]) #set the current POSI value to nonsense.
    sendcommand(COMM['HOME'],0) # this sleeps until it sees the status change from new_command

    #monitor the controller position and report at intervals of sleeptime
    if debug:
        print("goto:  Check position:");
    position=readback(ADDR['FPOS'])
    if debug:
        print("goto:  Check status:");
    status=STAT['BUSY']
    while status==STAT['BUSY']:
        status=readback(ADDR['STATUS'])
        hardstop1=readback(ADDR['HARD_STOP1'])
        hardstop2=readback(ADDR['HARD_STOP2'])
        home=readback(ADDR['HOME'])
        print("position:",readback(ADDR['FPOS'])," status:",status, "lb:",hardstop1, "hb:",hardstop2, "posi:",home)
        if debug:
            print ("goto: loop: check status:")
        status=readback(ADDR['STATUS'])
        time.sleep(sleeptime)

    #loop until controller busy flag is cleared
    home=readback(ADDR['HOME'])
    print("loop finished. final position:",readback(ADDR['FPOS'])," status:",status, "lb:",hardstop1, "hb:",hardstop2, "posi:",home)


    #report final position and success
    status=readback(ADDR['STATUS'])
    lb=readback(ADDR['HARD_STOP1'])
    hb=readback(ADDR['HARD_STOP2'])
    position=readback(ADDR['FPOS'])
    home=readback(ADDR['HOME'])
    turns=readback(ADDR['TURNS'])
    axis=readback(ADDR['XAXIS'])