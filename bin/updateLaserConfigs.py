#!/usr/bin/python3

import sys
import os
from quickAssign import writeXCD2
from quickReport import reportXCD2
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR

# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase


# tuning settings
sleeptime=0.5 #in seconds
debug=False
portsDb="xcd2_ports.kfdb"
PORTFILE="XCD_current_port"
logFile=""


def writeToFile( filename ):

    with open(filename, "w") as file:
        # go thru varDict
        for varName, varVal in ADDR.items():

            # report every variable from varDict
            check, trueVal = reportXCD2([varVal])

            if check==False:
                print("CRITICAL FAILURE. Communication error.")
                sys.exit()
        
            if debug:
                print("_readback result: ", trueVal[0])
        
            # Logs the change to the log for a change
            file.write('%s %s\n' % (varName, trueVal[0]))


    return 


def readFromFile( filename ):

    if not os.path.isfile(filename):
        print("Couldn't read from file. Variables not updated.")
        return False

    with open(filename, "r") as file:
        for line in file:
            (varName, varVal) = line.split()

            writeXCD2([ADDR[varName], varVal])
        
    return True



def updateLaserConfigs():
    return

if __name__ == "__main__":
    updateLaserConfigs()