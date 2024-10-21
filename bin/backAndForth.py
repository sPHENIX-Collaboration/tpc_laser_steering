#! /usr/bin/python3
#
# backAndForth.py can be used to continuously move back and forth between two 
# specified values

from quickReport import readback
from goto import goto
from changeAxisDogleg import changeAxis
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
import sys


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def backAndForth(axis, lb=None, hb=None, loop=True):

    #check to see if the target is a number.
    #if number: make it a float.
    #if no numbers input, then use low and high bound
    #otherwise return
    if (is_number(lb) and is_number(hb)):
        low=float(lb))
        high=float(hb)
    elif (lb==None) and (hb==None):
        low=readback(ADDR[''])
        high=readback(ADDR[''])
    else:
        print("backAndForth.py failed.  Argument format not correct - should be either 0 or 2 floating point values.")
        return


    while loop:
        goto(axis, dest1)
        goto(axis, dest2)
    return


if __name__ == "__main__":
    if len(sys.argv) == 2:
        axis=sys.argv[1]
        backAndForth(axis)
    elif len(sys.argv) == 4:
        axis=sys.argv[1] 
        low=sys.argv[2]
        high=sys.argv[3]
        backAndForth(axis, low, high)
    else:
        print("backAndForth.py failed.  Incorrect number of arguments.")
        sys.exit()
