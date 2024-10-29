#!/usr/bin/python3

import sys
import os
from quickAssign import writeXCD2
from quickReport import reportXCD2
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR

# to load tty data from the db so we know which tty we want:
sys.path.append("kfDatabase")
import kfDatabase

logFile=""

def logfileEntry():

    with open(logFile, "a") as file:
        file.write('{%s %s }' )

    return


if __name__ == "__main__":
    if len(sys.argv) == 1:
        logfileEntry()
    else:
        print("./logEntry.py NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("   ./changeAxisDogleg.py L#_DL#_A#")
