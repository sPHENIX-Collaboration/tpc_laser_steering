#! /usr/bin/python3
#
# wiggle.py takes a given motor axis and makes tiny motions to scan around
# the current or a given position
# create search script (waiting for user input) that scans thetaL in smallest possible steps for a given thetaS
# needs to tell us at each point where it is (report current position after each move)
# slow

from quickReport import readback
from goto import goto
from changeAxisDogleg import changeAxis
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
import sys


def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()} 
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print(f"_reverseLookup failed.  KeyError: {e}")
        sys.exit()
    return key  


def wiggle(axis, step, loop=True):
    position = readback(ADDR['FPOS'])
    dest1 = position - step
    dest2 = position + step
    
    goto(axis, dest1)
    goto(axis, dest2)

    return


if __name__ == "__main__":
    if len(sys.argv) == 2:
        axis=sys.argv[1]
        wiggle(axis)
    elif len(sys.argv) == 3:
        axis=sys.argv[1]
        step=sys.argv[2]
        wiggle(axis, step)
    else:
        print("wiggle.py failed.  Incorrect number of arguments.")
        sys.exit()
