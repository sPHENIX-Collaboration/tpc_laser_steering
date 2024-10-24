#! /usr/bin/python3
#
# backAndForth.py can be used to continuously move back and forth between two 
# specified values

from quickReport import readback
from goto import goto
from changeAxisDogleg import changeAxis
from backAndForth import backAndForth
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
import sys

def nestedBackAndForth(axis, lb, hb, amp_diff, steps):

    range = hb-lb
    midpt = range/2

    try:
        while True:
            for i in range(steps):
                
                lb_new = lb+steps*amp_diff
                hb_new = hb-steps*amp_diff
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