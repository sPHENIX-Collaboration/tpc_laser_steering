#! /usr/bin/python3
#
# nestedBackAndForth.py can be used to continuously move back and forth between two 
# specified values

from quickReport import readback
from goto import goto
from changeAxisDogleg import changeAxis
from backAndForth import backAndForth
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
import sys

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def nestedBackAndForth(axis, lb, hb, amp_diff, steps):

    if (is_number(lb) and is_number(hb)):
        low=float(lb)
        high=float(hb)
        amp=float(amp_diff)
        numSteps=int(steps)
    else:
        print("Input wrong")
        return

    span = high-low
    midpt = span/2

    try:
        while True:
            for i in range(numSteps):
                
                lb_new = low+i*amp
                hb_new = high-i*amp
                print("Performing nestedBackAndForth.py iteration ", i, ": ")
                backAndForth(axis, lb_new, hb_new, False)

    except KeyboardInterrupt:
        pass

    return

if __name__ == "__main__":
    if len(sys.argv) == 6:
        axis=sys.argv[1] 
        low=sys.argv[2]
        high=sys.argv[3]
        amplitude=sys.argv[4]
        steps=sys.argv[5]
        nestedBackAndForth(axis, low, high, amplitude, steps)
    else:
        print("nestedBackAndForth.py failed.  Incorrect number of arguments.")
        print("     ./nestedBackAndForth.py [axis] [lb] [hb] [min amplitude] [num steps]")
        sys.exit()