#!/usr/bin/python3

import subprocess
import json
import sys


def setPrecision(input, prec):
    rawDatum=float(input)
    scaleFactor=10**prec
    scaledDatum=int(rawDatum*scaleFactor)
    truncatedDatum=scaledDatum/scaleFactor
    if prec == 0:
        truncatedDatum=int(truncatedDatum)
    return scaledDatum,truncatedDatum

def parseJson(input,filename=None):
    data=json.loads(input)

    #print the json directly:
    if (filename):
        #print(filename)
        with open(filename,'w') as file:
            print(input, file=file)
                
 

    #data contains:
    header=data.get('header')
    lastcommand=None
    precision=None
    if header is None:
        print("no header found in input data")
        #fatal, because we need data on the precision to use.
        return
    
    version=header.get('version')
    if version is None:
        print("header does not have a version number!")
        #so at least we know it's crazy:
        version=-1

    lastCommand=header.get('last')
    if lastCommand is None:
        lastCommand="not found"
        #this isn't fatal, so we can continue
        
    precision=header.get('precision')
    if not precision:
        print("no information on precision found in header")
        #we can't do any scaling if there was no precision info.
        return

    benches=data.get('benches')
    if not benches:
        print("no benches found in input data")
        #this just means there's nothing to report.
        return
    #assemble the list of all axes in the json, and set the precision of all numbers
    cleanAxes={}
    truncAxes={}
    for benchName,benchAxes in benches.items():
        #print("bench:%s"%(benchName))
        for axisName,axis in benchAxes.items():
            cleanAxis={}
            truncAxis={}
            #cleanAxis['bench']=benchName
            #cleanAxis['axis']=axisName
            for key,value in axis.items():
                if key in precision:
                    #set the precision to the one in the header, then add to the axis dictionary
                    cleanValue,truncValue=setPrecision(value,precision[key])
                    cleanAxis[key]=cleanValue
                    truncAxis[key]=truncValue
                cleanAxes[axisName]=cleanAxis
                truncAxes[axisName]=truncAxis

    #print out the version:
    print("version")
    print(version)
                
    #print out the scale factors for future use, making sure to keep it in the same order as the axis data even if the header is not.
    print("order of variables is")
    if cleanAxes.values()!=[]:
        axisOrdering=next(iter(cleanAxes.values()))
        for key in axisOrdering.keys():
            print(key)
    else:
        print("not available because we have no benches")
    print("multiply data by 10^n (same order)")
    for key in axisOrdering.keys():
        #we only put items in cleanAxis if it was present in the precision dictionary, so this is safe:
        print(precision[key])
        
    #print out all the data as integers for rcdaq:    
    for axisName,axisData in cleanAxes.items():
        print(axisName)
        for value in axisData.values():
            print(value)

    #print the data in human-readable form:
    print("human:last py: %s\ttime:%s"%   (lastCommand,"no time")) 
    #loop over all benches and axes
    for axisName,a in truncAxes.items():
        print("human:%s (id=%s,axis=%s)\tCom=%s (arg=%s) Status=%s pos=%s\thome=%s lb=%s hb=%s turns=%s frp=%s frn=%s li=%s"%(axisName,a['ID'],a['XAXIS'],a['COMMAND'],a['ARG'],a['STATUS'],a['FPOS'],a['HOME'],a['HARD_STOP1'],a['HARD_STOP2'],a['TURNS'],a['FRP'],a['FRN'],a['LI']))
    #all done!
    return



    
if __name__ == "__main__":

    #v0: command=['ssh','pi@10.20.35.5','tail -n 2 ~/XCDCommandCodes/bin/masterLog | head -n 1']
    #for testing: command=['cat','dummy_v2.json']
    command=['ssh','pi@10.20.35.5','~/XCDCommandCodes/bin/collect_logs.py']
    #command=['echo','hello world']
    result = subprocess.run(command, capture_output=True, text=True)
    if (result.stderr==""):
        if len(sys.argv)==1:
            #if no arguments, generate output, do not generate json output
            parseJson(result.stdout)
        elif len(sys.argv)==2:
            #if there's an argument, write the json to that file the dummy instead:
            parseJson(result.stdout,sys.argv[1])
        else:
            print("wrong args.  can't get laser data") 

    
