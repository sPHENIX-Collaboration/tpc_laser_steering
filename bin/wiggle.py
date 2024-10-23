#! /usr/bin/python3
#
# wiggle.py takes a given motor axis and makes tiny motions around the current position 
# to scan around for 
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


def wiggle(axis, step):

    position = readback(ADDR['FPOS'])
    dest1 = position - step
    dest2 = position + 2*step
    
    s1, pos1 = goto(axis, dest1)
    if not s1:
        print("FAIL wiggle.py move forward")
    x = input("---wiggle.py forward performed.  At position ", readback(ADDR['FPOS']), ".  Wiggle other direction? [y/n]")
    if x == "n":
        return
    s2, pos2 = goto(axis, dest2)
    if not s2:
        print("FAIL wiggle.py move backward")
    
    print("---wiggle.py back performed.  At position ", readback(ADDR['FPOS']), ".")

    return


if __name__ == "__main__":
    if len(sys.argv) == 3:
        axis=sys.argv[1]
        step=sys.argv[2]
        wiggle(axis, step)
    else:
        print("wiggle.py failed.  Incorrect number of arguments.")
        sys.exit()
