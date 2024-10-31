#!/bin/python3

import subprocess
import json

command=['ssh','pi@10.20.35.5','tail -n 2 ~/XCDCommandCodes/bin/masterLog | head -n 1']
#command=['echo','hello world']
result = subprocess.run(command, capture_output=True, text=True)
print(result.stdout)
if (result.stderr==""):
    data=json.loads(result.stdout)
    #data contains 
    #bench contains 8 axis contains d
    #for bench in data
    #for axis in bench
    d=['ID','XAXIS','COMMAND','ARG','STATUS','HOME','HARD_STOP1','HARD_STOP2','TURNS','FPOS']
    #for sanity checks, we include some extra digits on the things that should be integers.
    #this is the number of digits after the decimal that we keep:
    dataPrec=[2,2,2,5,2,5,5,5,2,5,5]
    isInt=   [1,1,1,0,1,0,0,0,1,0,0]
    repData=[-1000]*10
    #p is the processed data, once each item has been truncated to a suitable depth. 
    p=[-1000]*10

    #todo:  with open(filename,w):
    print("data format version for our own future sanity as we develop this: 0\n0");
    #todo:  with open(filename,a):
    #and tab eeeeeeverything in.  phaw.

    #todo:  get the calibrated phi position in TPC coordinates and display the local phi wrt that.  Or wrt 'pointing inward' maybe, since that respects the symmetries
    #todo:  get the calibrated theta positions wrt z axis in degrees.    
    dataCorrupted=0
    for i in range(10):
        rawDatum=float(data[d[i]])
        scaleFactor=10**dataPrec[i]
        scaledDatum=int(rawDatum*scaleFactor)
        truncatedDatum=scaledDatum/scaleFactor
        #save our processed data for future use
        p[i]=truncatedDatum
        #sanity check things that should be integers, but display them just as integers
        intReply=""
        residual=0
        if isInt[i]:
            residual=int((rawDatum-truncatedDatum)*scaleFactor)
            if (not residual==0):
                intReply=" Residual is %s! readback corrupted!"
                dataCorrupted=1
            scaledDatum=int(truncatedDatum)
            scaleFactor=1
            p[i]=scaledDatum
        print("Readback of %s=%s %s.\nMantissa:\n%s\nMultiplier\n%s\nSanity Check Residual:\n%s"%(d[i],truncatedDatum,intReply,scaledDatum,scaleFactor,residual))
   #todo:  built a full list of commands that is flat so we can figure out what command is running without having to know what kind of axis we are on first.    
    print("Human Readable:")
    print("last py: %s args: %s time:%s"%   ("not","yet implemented","no time")) 
    #loop over all benches and axes
    print("ChannelID:%s (axis=%s)\tCom=%s (arg=%s)\tStatus=%s\thome=%s\tlb=%s\thb=%s\tturns=%s\tpos=%s"%(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9])    
                       
