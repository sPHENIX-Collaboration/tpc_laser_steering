#!/usr/bin/python3

import sys
import os
from quickAssign import writeXCD2
from quickReport import reportXCD2
from changeAxisDogleg import changeAxis
from goto import goto
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR

def coordinateSearch(axis, lb_PH=None, hb_PH=None, numPts_PH, lb_TH=None, hb_TH=None, numPts_TH):

    phiAxis = axis+"_PH"
    thsAxis = axis+"_TH_S"
    thlAxis = axis+"_TH_L"

    didChange = changeAxis()
    (phiAxis, )
    didChange = changeAxis()
    goto()
    (thsAxis, )

    return

if __name__ == "__main__":
    if len(sys.argv) == 4:
        axis=sys.argv[1]
        coordinateSearch(axis, )
    elif len(sys.argv) == 8:
        axis=sys.argv[1]
        lb_PH=sys.argv[2]
        hb_PH=sys.argv[3]
        numPts_PH=sys.argv[4]
        coordinateSearch(axis,)
    else:
        print("coordinateSearch.py NOT EXECUTED.  Incorrect number of arguments.  Correct usage is:")
        print("     ./coordinateSearch.py  [axis]  [numPts_PH]  [numPts_TH]       OR")
        print("     ./coordinateSearch.py  [axis]  [lb_PH]  [hb_PH]  [numPts_PH]  []  []  []")
        sys.exit()