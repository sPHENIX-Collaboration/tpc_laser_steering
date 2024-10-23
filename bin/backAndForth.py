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
        low=float(lb)
        high=float(hb)
    elif (lb==None) and (hb==None):
        low=readback(ADDR['HARD_STOP1'])
        high=readback(ADDR['HARD_STOP2'])
    else:
        print("backAndForth.py failed.  Argument format not correct - function call should be followed by either 0 or 2 floating point values.")
        return

    #unless user interrupts program by hitting keyboard
    #backAndForth will now loop between the low and high bound
    try: 
        while loop:
            #move to low bound
            print("----backAndForth.py moving axis ", axis, " to low bound")
            s1, val1 = goto(axis, low)
            if not s1:
                print("backAndForth.py failed to move to low bound ", str(lb)," successfully.  Program will continue unless force quit.")
            
            #move to high bound
            print("----backAndForth.py moving axis ", axis, " to high bound")
            s2, val2 = goto(axis, high)
            if not s2:
                print("backAndForth.py failed to move to high bound ", str(hb)," successfully.  Program will continue unless force quit.")
    except KeyboardInterrupt:
        pass

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
