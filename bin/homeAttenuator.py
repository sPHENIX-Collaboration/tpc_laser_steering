#!/usr/bin/python3

from quickAssign import sendcommand, writeXCD2
from quickReport import readback
import sys
import time
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varAttenuatorCommands as COMM


# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase


#tuning settings
sleeptime = 0.5 # in seconds
timeout = 10    # in seconds
debug=False
mainDb="test_only_axis_parameters.kfdb"
matchTolerance=0.01


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

def homeAttenuator(referenceEgg):    
    #check if controller is busy.  If so, exit with explanation
    if debug:
        print("goto:  Check status:")
    status=readback(ADDR['STATUS'])

    if status!=0:
        print("NOT EXECUTED. Controller status is not 0.")
        return False, 0,0,0
        #sys.exit()

    writeXCD2([ADDR['HOME'],-999])
    sendcommand(COMM['HOME'],0) # this sleeps until it sees the status change from new_command

    #monitor the controller position and report at intervals of sleeptime
    if debug:
        print("goto:  Check position:");
    position=readback(ADDR['FPOS'])
    if debug:
        print("goto:  Check status:");
    status=STAT['BUSY']
    t1=time.time()
    while status==STAT['BUSY']:
        status=readback(ADDR['STATUS'])
        hardstop1=readback(ADDR['HARD_STOP1'])
        hardstop2=readback(ADDR['HARD_STOP2'])
        home=readback(ADDR['HOME'])
        print("position:",readback(ADDR['FPOS'])," status:",status, "lb:",hardstop1, "hb:",hardstop2, "home:",home)
        if debug:
            print ("home: loop: check status:")
        status=readback(ADDR['STATUS'])
        time.sleep(sleeptime)
        
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
        
    homeIsReal=False
    if (home>hardstop1 and home<hardstop2):
        homeIsReal=True   
    if not homeIsReal:
        home=hardstop1
    lbRel=hardstop1-home
    hbRel=hardstop2-home
    posRel=position-home
    span=hardstop2-hardstop1

    #sanity check
    if(span<0.75):
        print("FAIL.  Span is less than 0.75 (expect ~0.80).  Motor likely jammed.  span:%s. lbrel:%s hbrel:%s posi:%s%s%s."%(span,lbRel,hbRel, home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))
        print("aborting.  Db will not be updated.")
        return False, hardstop1,hardstop2,home
        sys.exit()
    if(span>1.0):
        print("FAIL.  Span is greater than 1?!?  Encoder likely damaged.  span:%s. lbrel:%s hbrel:%s posi:%s%s%s."%(span,lbRel,hbRel, home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))
        print("aborting.  Db will not be updated.")
        return False, hardstop1,hardstop2,home
    if(abs(hardstop1-position)>matchTolerance):
        print("FAIL.  lowbound and return to lowbound are not the same?  Motor likely jammed.  posRel:%s. lbrel:%s hbrel:%s posi:%s%s%s."%(posRel,lbRel,hbRel, home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))
        print("aborting.  Db will not be updated.")
        return False, hardstop1,hardstop2,home
    #compare to db values

    if referenceEgg!=None:
        print("Comparing to Db.  Current status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f posi:%1.7f%s%s(should be zero)"%(status,_reverseLookup(STAT,status),position,axis, turns,lb,hb,home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))
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
                print("FAIL.  Readback-db residuals are larger than tolerance %s:\n\tspan:%s-%s=%s.\n\tlbrel:%s-%s=%s.\n\thbrel:%s-%s=%s"%(matchTolerance,span,spanDb,varSpan,lbRel,lbRelDb,varLb,hbRel,hbRelDb,varHb))
                print("   This does not match the expectations for %s.  If you are sure this really is %s, and want to update %s with new parameters, run the following commands:"%(referenceEgg,referenceEgg,mainDb))
            if  (not present[0] or not present[1] or not present[2]):
                print("FAIL.  Not all values are in the database for egg %s."%(referenceEgg))
                print("   This does not match the expectations for %s.  If you are sure this really is %s, and want to update %s with new parameters, run the following commands:"%(referenceEgg,referenceEgg,mainDb))
            print("   ./kfDatabase/kfDatabase.py %s %s/%s %f %s"%(mainDb,referenceEgg,"home",0.0,"new"*(not present[0])))
            print("   ./kfDatabase/kfDatabase.py %s %s/%s %f %s"%(mainDb,referenceEgg,"lowbound",lbRel,"new"*(not present[1])))
            print("   ./kfDatabase/kfDatabase.py %s %s/%s %f %s"%(mainDb,referenceEgg,"highbound",hbRel,"new"*(not present[2])))
        elif match:
            print("SUCCESS.  Readback-db residuals are within tolerance %s:\n\tspan:%s-%s=%s.\n\tlbrel:%s-%s=%s.\n\thbrel:%s-%s=%s."%(matchTolerance,span,spanDb,varSpan,lbRel,lbRelDb,varLb,hbRel,hbRelDb,varHb))
        print("Setting current position to distance from home(POSI) and updating onboard hardstops.")
        writeXCD2([ADDR['FPOS'], posRel])
        writeXCD2([ADDR['HARD_STOP1'], lbRel])
        writeXCD2([ADDR['HARD_STOP2'], hbRel])
        writeXCD2([ADDR['HOME'],0.0])
    
        lb=readback(ADDR['HARD_STOP1'])
        hb=readback(ADDR['HARD_STOP2'])
        position=readback(ADDR['FPOS'])   
        home=readback(ADDR['HOME'])
    result=match or (not present[0] or not present[1] or not present[2]) or referenceEgg==None    
    
    if status==STAT['READY'] and result==True:
        print("SUCCESS. homeAttenuator complete. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f home:%1.5f%s%s"%(status,_reverseLookup(STAT,status),position,axis, turns,lb,hb, home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))
    else:
        print("FAIL. homeAttenuator failed. status: %s (%s) position:%1.6f axis:%s turns:%s lb:%1.5f hb:%1.5f home:%1.5f%s%s"%(status,_reverseLookup(STAT,status),position,axis, turns,lb,hb,home,"(Real)"*homeIsReal,"(NotFound)"*(not homeIsReal)))
    return result, lb,hb,home


    
if __name__ == "__main__":

    #check args
    referenceEgg=None
    if len(sys.argv) == 2: #note that sys.argv has arg 1 as the command itself
        referenceEgg=sys.argv[1]
    elif len(sys.argv) == 1: #note that sys.argv has arg 1 as the command itself
        referenceEgg=None
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is ./homePhi.py or ./homePhi.py Egg")
        sys.exit()
    homeAttenuator(referenceEgg)
