#! /usr/bin/python3
#
# for a given pair of thetas
# can input desired position
# if already at desired starting position, don't enter in values
# start by moving theta long to edge ()

import sys
from quickReport import readback
from goto import goto
from changeAxisDogleg import changeAxis
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR


def inchworm(thS_start=None, thL_start=None):

    if thS_start==None or thL_start==None:

    else:
        x = input("Press enter to perform next move.  Press any key then enter to abort.")
        if x != "":
            return
    
    return


if __name__ == "__main__":
    if len(sys.argv) == 3:
        thS_i=sys.argv[1]
        thL_i=sys.argv[2]
        inchworm(thS_i, thL_i)
    elif len(sys.argv) == 1:
        inchworm()
    else:
        print("wiggleAxis.py failed.  Incorrect number of arguments.")
        sys.exit()