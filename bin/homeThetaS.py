#!/usr/bin/python3

from quickAssign import sendcommand, writeXCD2
from quickReport import readback
import sys
import time
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varThetaSCommands as COMM


# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase

#tuning settings
mainDb="axis_parameters.kfdb"
sleeptime=0.1 #in seconds
debug=False



def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print("reverse lookup failed.  KeyError: %s"%(e))
        sys.exit()
    return key



def homeThetaS(referenceEgg=None):
    #check if controller is busy.  If so, exit with explanation
    if debug:
        print("homeThetaS:  Check status:")
    status=readback(ADDR['STATUS'])

    if status!=0:
        print("NOT EXECUTED. Controller status is not 0.")
        return False,0,0,0


    dummyHome=-1000
    writeXCD2([ADDR['HOME'],dummyHome]) #set the current POSI value to nonsense.

    sendcommand(COMM['HOME'],0) # this sleeps until it sees the status change from new_command

    #monitor the controller position and report at intervals of sleeptime
    if debug:
        print("homeThetaS:  Check position:");
    position=readback(ADDR['FPOS'])
    if debug:
        print("homeThetaS:  Check status:");
    status=STAT['BUSY']
    print("homeThetaS:  first pass")
    while status==STAT['BUSY']:
        status=readback(ADDR['STATUS'])
        hardstop1=readback(ADDR['HARD_STOP1'])
        hardstop2=readback(ADDR['HARD_STOP2'])
        home=readback(ADDR['HOME'])
        print("position:",readback(ADDR['FPOS'])," status:",status, "lb:",hardstop1, "hb:",hardstop2, "home:",home)

        if debug:
            print ("homeThetaS: loop: check status:")
        time.sleep(sleeptime)
    #loop until controller busy flag is cleared

    #set position to the correct offset from the measured home.  This means the next time we find home, it should be at +1.0
    position=readback(ADDR['FPOS'])   
    home=readback(ADDR['HOME'])   
    writeXCD2([ADDR['FPOS'], position-home])
    writeXCD2([ADDR['HOME'],0.0])

    #now do it again.  if home moves by exactly +1, we know it is real and reliable.
    sendcommand(COMM['HOME'],0) # this sleeps until it sees the status change from new_command
    status=STAT['BUSY']
    print("homeThetaS:  second pass.  Defined home is 0.0")
    while status==STAT['BUSY']:
        status=readback(ADDR['STATUS'])
        hardstop1=readback(ADDR['HARD_STOP1'])
        hardstop2=readback(ADDR['HARD_STOP2'])
        home=readback(ADDR['HOME'])
        print("position (recheck):",readback(ADDR['FPOS'])," status:",status, "lb:",hardstop1, "hb:",hardstop2, "home:",home)

        if debug:
            print ("homeThetaS: loop: check status:")
        time.sleep(sleeptime)
    #loop until controller busy flag is cleared


    #report final position and success
    if debug:
        print ("homeThetaS: finishing up.  check status and readback:")

    position=readback(ADDR['FPOS'])   
    print("Setting POSI position to zero and updating onboard hardstops.  POSI Offset was %s from previous home"%(home))
    writeXCD2([ADDR['FPOS'], position-home])
    writeXCD2([ADDR['HARD_STOP1'], -1.0])
    writeXCD2([ADDR['HARD_STOP2'], 1.0])
    lb=readback(ADDR['HARD_STOP1'])
    hb=readback(ADDR['HARD_STOP2'])
    position=readback(ADDR['FPOS'])   
    turns=readback(ADDR['TURNS'])
    axis=readback(ADDR['XAXIS'])   

    if debug:
        print ("home: finishing up.  check status and readback:")

    homeIsReal=True
    homeIsConsistent=False
    if (home==0.0):
        homeIsReal=False
    if (home==1.0 or home ==-1.0):
        homeIsConsistent=True
        home=0.0
    #sanity check
    if(not homeIsReal or not homeIsConsistent):
        print("FAIL.  Home does not match the previous home.  Encoder is not reading back correctly, or home is damaged.  lb:%s hb:%s posi:%s%s%s."%(lb,hb, home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))
        print("aborting.  Db will not be updated.")
        return False,0,0,0



    #compare to db values
    if referenceEgg!=None:
        print("Comparing to Db.  Current status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f home:%s%s%s"%(status,_reverseLookup(STAT,status),position,axis, turns,lb,hb, home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))

        match=True
        present=[True]*1
        success,homeDb=kfDatabase.readVar(mainDb,"%s/home"%referenceEgg)
        if not success:
            print("Can't find home for %s in %s"%(referenceEgg,mainDb))
            match=False
            present[0]=False
        if home != homeDb:
            match=False
        if not match:
            if  (present[0]):
                print("FAIL.  Home is not zero in the db for some reason.  home:%s homeDb:%s.  residual:%s"%(home,homeDb,home-homeDb))
                print("   This does not match the expectations for %s.  If you are sure this really is %s, and want to update %s with new parameters, run the following command:"%(referenceEgg,referenceEgg,mainDb))
            if  (not present[0] ):
                print("FAIL.  Not all values are in the database for egg %s."%(referenceEgg))
                print("   This does not match the expectations for %s.  If you are sure this really is %s, and want to update %s with new parameters, run the following command:"%(referenceEgg,referenceEgg,mainDb))
            print("   ./kfDatabase/kfDatabase.py %s %s/%s %f %s"%(mainDb,referenceEgg,"home",0.0,"new"*(not present[0])))
            print("   NOTE:  If there are values for diode positions, these will move by the residuals above as well.")
        elif match:
            print("SUCCESS.  Home matches db.home:%s homeDb:%s.  residual:%s"%(home,homeDb,home-homeDb))
        print("Setting current position relative to home and updating onboard hardstops.")
        
        lb=readback(ADDR['HARD_STOP1'])
        hb=readback(ADDR['HARD_STOP2'])
        position=readback(ADDR['FPOS'])   
        

    if status==STAT['READY']:
        print("SUCCESS. homeThetaS complete. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f home(before):%1.5f"%(status,_reverseLookup(STAT,status),position,axis, turns,lb,hb, home))
        return True,lb,hb,home
    else:
        print("FAIL. homeThetaS failed. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f home(before):%1.5f"%(status,_reverseLookup(STAT,status),position,axis, turns,lb,hb,home))
        return True,lb,hb,home


if __name__ == "__main__":
    #check args
    referenceEgg=None
    if len(sys.argv) == 2: #note that sys.argv has arg 1 as the command itself
        referenceEgg=sys.argv[1]
        homeThetaS(referenceEgg)
    elif len(sys.argv) == 1: #note that sys.argv has arg 1 as the command itself
        homeThetaS()
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is ./homeThetaS.py or ./homeThetaS.py Egg_TH_S")
        sys.exit()
    #if wrong arguments, exit with explanation
