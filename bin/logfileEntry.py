#!/usr/bin/python3

import sys
import os
from quickReport import reportXCD2, readback
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR

# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase

debug=False
logFile="masterLog"

def logfileEntry(dummyName=None, dummyVal=None):

    with open(logFile, "a") as file:
        file.write('{')
    
        for varName, varVal in ADDR.items():

                # report every variable from varDict
                check, trueVal = reportXCD2([varVal])

                if check==False:
                    print("CRITICAL FAILURE. Communication error.")
                    sys.exit()
            
                if debug:
                    print("_readback result: ", trueVal[0])
            
                # Logs the change to the log for a change
                file.write('\'%s\':%s, ' % (varName, trueVal[0]))
        
        file.write('\'statusCODE\':%s}' % readback(ADDR['STATUS']))

    return


if __name__ == "__main__":
    if len(sys.argv) == 1:
        logfileEntry()
    else:
        print("./logfileEntry.py NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("     ./logfileEntry()")
