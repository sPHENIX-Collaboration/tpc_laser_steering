#!/usr/bin/python3

import sys
import os
from xcdSerial import getCurrentPort
from quickReport import readback
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varUniqueID as AXID

debug=False
logDirectory="/home/pi/XCDCommandCodes/bin/axisLogs/"

# need axis to be in format 9N_TH_S
# logfile needs USB port too for posterity
# logfile needs to write all data to specific axis (motor) logfile
# format as 9N_##.log
# how do we collect most up-to-date info?
# collect_logs -tail -2 > head -1 to 

def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print(f"gotoDogleg lookup failed.  KeyError: {e}")
        sys.exit()
    return key  


def logfileEntry():

    axisID = readback(ADDR['ID'])
    axis = _reverseLookup(AXID, axisID)

    filename = logDirectory + axis
    with open(filename, "a") as file:
        file.write('{\"USBport\":\"%s\"' % (getCurrentPort()))
    
        for varName, varVal in ADDR.items():
                
            # readback each variable in ADDR dictionary
            trueVal=readback(varVal)
        
            if debug:
                print("_readback result: ", trueVal)

            # Logs the change to the log for a change
            file.write(',\"%s\":%s' % (varName, trueVal))
        
        file.write('} \n')

    return True


if __name__ == "__main__":
    if len(sys.argv) == 1:
        logfileEntry()
    else:
        print("./logfileEntry.py NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("     ./logfileEntry.py")
        sys.exit()
