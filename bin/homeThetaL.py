#!/usr/bin/python3

from quickAssign import sendcommand, writeXCD2
from quickReport import readback
import sys
import time
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varThetaLCommands as COMM


# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase

#tuning settings
mainDb="axis_parameters.kfdb"
sleeptime=0.1 #in seconds
debug=False
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



def homeThetaL(referenceEgg=None):
    #check if controller is busy.  If so, exit with explanation
    if debug:
        print("homeThetaL:  Check status:")
    status=readback(ADDR['STATUS'])

    if status!=0:
        print("NOT EXECUTED. Controller status is not 0.")
        return False,0,0,0


    dummyHome=-1000
    writeXCD2([ADDR['HOME'],dummyHome]) #set the current POSI value to nonsense.
    sendcommand(COMM['HOME'],0) # this sleeps until it sees the status change from new_command

    #monitor the controller position and report at intervals of sleeptime
    if debug:
        print("homeThetaL:  Check position:");
    position=readback(ADDR['FPOS'])
    if debug:
        print("homeThetaL:  Check status:");
    status=STAT['BUSY']
    while status==STAT['BUSY']:
        status=readback(ADDR['STATUS'])
        hardstop1=readback(ADDR['HARD_STOP1'])
        hardstop2=readback(ADDR['HARD_STOP2'])
        home=readback(ADDR['HOME'])
        print("position:",readback(ADDR['FPOS'])," status:",status, "lb:",hardstop1, "hb:",hardstop2, "posi:",home)

        if debug:
            print ("homeThetaL: loop: check status:")
        time.sleep(sleeptime)

    ######


    #loop until controller busy flag is cleared


    #report final position and success
    status=readback(ADDR['STATUS'])
    lb=readback(ADDR['HARD_STOP1'])
    hb=readback(ADDR['HARD_STOP2'])
    position=readback(ADDR['FPOS'])
    home=readback(ADDR['HOME'])
    turns=readback(ADDR['TURNS'])
    axis=readback(ADDR['XAXIS'])

    if debug:
        print ("home: finishing up.  check status and readback:")

        
    lbRel=hardstop1-home
    hbRel=hardstop2-home
    posRel=position-home
    span=hardstop2-hardstop1
    homeIsReal=False
    if (home>hardstop1 and home<hardstop2):
        homeIsReal=True

    #sanity check
    if(span<0.55):
        print("FAIL.  Span is less than 0.55 (expect ~0.60).  Motor likely jammed.  span:%s. lbrel:%s hbrel:%s posi:%s%s%s."%(span,lbRel,hbRel, home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))
        print("aborting.  Db will not be updated.")
        return False,0,0,0
    if(span>0.75):
        print("FAIL.  Span is greater than 0.75.  Encoder damaged, or axis wrong, or light pipe not present?.  span:%s. lbrel:%s hbrel:%s posi:%s%s%s."%(span,lbRel,hbRel, home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))
        print("aborting.  Db will not be updated.")
        return False,0,0,0




    #compare to db values
    if referenceEgg!=None:
        print("Comparing to Db.  Current status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f home:%s%s%s"%(status,_reverseLookup(STAT,status),position,axis, turns,lb,hb, home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))

        match=True
        present=[True]*3
        success,homeDb=kfDatabase.readVar(mainDb,"%s/home"%referenceEgg)
        if not success:
            print("Can't find home for %s in %s"%(referenceEgg,mainDb))
            match=False
            present[0]=False
        success,lbDb=kfDatabase.readVar(mainDb,"%s/lowbound"%referenceEgg)
        if not success:
            print("Can't find lb for %s in %s"%(referenceEgg,mainDb))
            match=False
            present[1]=False
        success,hbDb=kfDatabase.readVar(mainDb,"%s/highbound"%referenceEgg)
        if not success:
            print("Can't find hb for %s in %s"%(referenceEgg,mainDb))
            match=False
            present[2]=False
        spanDb=hbDb-lbDb
        span=hardstop2-hardstop1
        lbRelDb=lbDb-homeDb
        hbRelDb=hbDb-homeDb
        varLb=lbRel-lbRelDb
        varHb=hbRel-hbRelDb
        varSpan=span-spanDb
        if (
            abs(varLb)>matchTolerance or
            abs(varHb)>matchTolerance or
            abs(varSpan)>matchTolerance
        ):
            match=False
        if not match:
            if  (present[0] and present[1] and present[2]):
                print("FAIL.  Readback-db residuals are larger than tolerance %s:\n\tspan:%s-%s=%s.\n\tlbrel:%s-%s=%s.\n\thbrel:%s-%s=%s."%(matchTolerance,span,spanDb,varSpan,lbRel,lbRelDb,varLb,hbRel,hbRelDb,varHb))
                print("   This does not match the expectations for %s.  If you are sure this really is %s, and want to update %s with new parameters, run the following commands:"%(referenceEgg,referenceEgg,mainDb))
            if  (not present[0] or not present[1] or not present[2]):
                print("FAIL.  Not all values are in the database for egg %s."%(referenceEgg))
                print("   This does not match the expectations for %s.  If you are sure this really is %s, and want to update %s with new parameters, run the following commands:"%(referenceEgg,referenceEgg,mainDb))
            print("   ./kfDatabase/kfDatabase.py %s %s/%s %f %s"%(mainDb,referenceEgg,"home",0.0,"new"*(not present[0])))
            print("   ./kfDatabase/kfDatabase.py %s %s/%s %f %s"%(mainDb,referenceEgg,"lowbound",lbRel,"new"*(not present[1])))
            print("   ./kfDatabase/kfDatabase.py %s %s/%s %f %s"%(mainDb,referenceEgg,"highbound",hbRel,"new"*(not present[2])))
            print("   NOTE:  If there are values for diode positions, those may move by the POSI residual as well.")
        elif match:
            print("SUCCESS.  Readback-db residuals are within tolerance %s:\n\tspan:%s-%s=%s.\n\tlbrel:%s-%s=%s.\n\thbrel:%s-%s=%s."%(matchTolerance,span,spanDb,varSpan,lbRel,lbRelDb,varLb,hbRel,hbRelDb,varHb))
        print("Setting current position relative to home and updating onboard hardstops.")
        writeXCD2([ADDR['FPOS'], posRel])
        writeXCD2([ADDR['HARD_STOP1'], lbRel])
        writeXCD2([ADDR['HARD_STOP2'], hbRel])
        
        lb=readback(ADDR['HARD_STOP1'])
        hb=readback(ADDR['HARD_STOP2'])
        position=readback(ADDR['FPOS'])   
        

    if status==STAT['READY']:
        print("SUCCESS. homeThetaL complete. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f home(before):%1.5f"%(status,_reverseLookup(STAT,status),position,axis, turns,lb,hb, home))
        return True,lb,hb,home
    else:
        print("FAIL. homeThetaL failed. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f home(before):%1.5f"%(status,_reverseLookup(STAT,status),position,axis, turns,lb,hb,home))
        return True,lb,hb,home


if __name__ == "__main__":
    #check args
    if len(sys.argv) == 2: #note that sys.argv has arg 1 as the command itself
        referenceEgg=sys.argv[1]
        homeThetaL(referenceEgg)
    elif len(sys.argv) == 1: #note that sys.argv has arg 1 as the command itself
        homeThetaL()
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is ./homeThetaL.py or ./homeThetaL.py Egg_TH_L")
        sys.exit()
    #if wrong arguments, exit with explanation
