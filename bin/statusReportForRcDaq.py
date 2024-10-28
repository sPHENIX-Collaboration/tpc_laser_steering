#!/usr/bin/python3

# This is designed to read back the status of all axes for recording in RCDAQ
# Right now, this only reads back the current active axis
# TODO:  We do not attempt to change axis currently.  We need to make sure this
# does not cause conflicts with commands sent to the controller.
# Alternatively, instead of running this from ssh, this command could run at the
# end of every goto/motion, cat'ing into a file, and the resulting file could be
# cat'd by the ssh command instead.

from quickAssign import sendcommand,writeXCD2
from quickReport import readback
import sys
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varUniqueID as AXISID


def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print(f"_reverseLookup failed.  KeyError: {e}")
        sys.exit()
    return key  

def reportAllAxisDummyTest():
    #todo:  with open("temp/last_axis_data_0_0",w)
    print("1 hello\n1\n2 world\n3\n4\n5")
    return

def reportAllAxis(axis):
    #currently we can only talk to the current port without possibly messing up the ongoing commands.  Need to think about this.
    #to reduce the number of calls, we collect the commands in a single readback request:
    #dataname, it just got cumbersome to keep typing that out.
    d=['ID','XAXIS','COMMAND','ARG','STATUS','HOME','HARD_STOP1','HARDSTOP2','TURNS','FPOS','(delta)']
    
    #for sanity checks, we include some extra digits on the things that should be integers.
    #this is the number of digits after the decimal that we keep:
    dataPrec=[2,2,2,2,5,5,5,5,2,5,5]
    isInt=   [1,1,1,1,0,0,0,0,1,0,0]
    repData=[-1000]*11
    #p is the processed data, once each item has been truncated to a suitable depth. 
    p=[-1000]*11

    #the call:
    repOk,repData=reportXCD2specifyAxis(axis,ADDR[d[0]],ADDR[d[1]],ADDR[d[2]],ADDR[d[3]],ADDR[d[4]],ADDR[d[5]],ADDR[d[6]],ADDR[d[7]],ADDR[d[8]],ADDR[d[9]])
    #and a follow up to get a sense of whether we're moving
    repOk2,repData2=reportXCD2specifyAxis(axis,ADDR['FPOS'])
    #set the tenth value to the delta
    repData[10]=repData2[0]-repData[9]
    #set our position to the latest one (slightly more correct)
    repData[9]=repData2[0]
    #todo: filename="temp/last_axis_data_%s_%s"%(channel,axis)
    #todo:  with open(filename,w):
    print("data format version for our own future sanity as we develop this: 0\n0");
    #todo:  with open(filename,a):
    #and tab eeeeeeverything in.  phaw.
    if (not repOk):
        print("Readback status:  axis %s readback failed. (any lost items are = -1000).\n0"%axis)

    else:
        print("Readback status:  axis %s readback successful.\n1")
        print("1")

    #todo:  get the calibrated phi position in TPC coordinates and display the local phi wrt that.  Or wrt 'pointing inward' maybe, since that respects the symmetries
    #todo:  get the calibrated theta positions wrt z axis in degrees.
    
    dataCorrupted=0
    for i in range(11):
        scaleFactor=10**dataPrec[i]
        scaledDatum=int(float(repData[i])*scaleFactor)
        truncatedDatum=scaledDatum/scaleFactor
        #save our processed data for future use
        p[i]=truncatedDatum
        #sanity check things that should be integers, but display them just as integers
        intReply=""
        residual=0
        if isInt[i]:
            residual=repData[i]-truncatedDatum
            if (not residual==0):
                intReply=" Residual is %s! readback corrupted!"
                dataCorrupted=1
            scaledDatum=truncatedDatum
            scaleFactor=1
        print("Readback of %s=%s %s.\nMantissa:\n%s\nMultiplier\n%s\nSanity Check Residual:\n%s"%(d[i],truncatedDatum,inReply,scaledDatum,scaleFactor,residual))

    #todo:  built a full list of commands that is flat so we can figure out what command is running without having to know what kind of axis we are on first.    
    print("Human Readable:")
    print("ChannelID:%s (axis=%s)\tCommand=%s(%s)\tStatus=%s"%(_reverseLookup(AXISID,p[0]),p[1],p[2],p[3],p[4]))
    print("Axis Values: home=%s\tlb=%s\thb=%s\tturns=%s"%(p[5],p[6],p[7],p[8]))
    print("Axis Motion: pos=%s\tdelta=%s (motion between two consecutive FPOS reports)"%(p[9],p[10]))
    return



if __name__ == "__main__":
    #check args
    if len(sys.argv)==1:
        #if no arguments, report back both axes
        reportAllAxis(0)
        reportAllAxis(1)
    elif len(sys.argv)==2:
        #if there's an argument, run the dummy instead:
        reportAllAxisDummyTest()
    else:
        print("for automated recognition that the call failed,report version=-1 and status=0\n-1\n0")
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("   ./statusReportForRcDaq.py testingonly")
        print("   ./statusReportForRcDaq.py")
    sys.exit()
