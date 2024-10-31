#!/usr/bin/python3

import sys
import os
import time
from quickAssign import writeXCD2
from quickReport import reportXCD2, readback
from changeAxisDogleg import changeAxis
from aimAt import aimAt
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR

debug=False
sleeptime=30

def coordinateSearch(axis, numPts_PH, numPts_TH, lb_PH=None, hb_PH=None, lb_TH=None, hb_TH=None):

    if numPts_PH<=1 or numPts_TH<=1:
        return

    phiAxis = axis+"_PH"
    thsAxis = axis+"_TH_S"
    thlAxis = axis+"_TH_L"

    if lb_PH == None:
        didChange = changeAxis(phiAxis)
        if not didChange:
            print("Could not get phi bounds")
            return
        lb_PH = 360*readback(ADDR['HARD_STOP1'])
    if hb_PH == None:
        hb_PH = 360*readback(ADDR['HARD_STOP2'])
    if lb_TH == None:
        lb_TH = 10
    if hb_TH == None:
        hb_TH = 30

    phi_arr = [0.0]*numPts_PH
    phi_space=(hb_PH-lb_PH)/(numPts_PH-1)
    for i in range(numPts_PH):
        phi_arr[i]=lb_PH+i*phi_space

    th_arr = [0.0]*numPts_TH
    th_space=(hb_PH-lb_TH)/(numPts_TH-1)
    for i in range(numPts_PH):
        th_arr[i]=lb_TH+i*th_space

    for th in th_arr:
        aimAt(axis, axis, th, None)
        for phi in phi_arr:
            aimAt(axis, axis, None, phi)
            time.sleep(sleeptime)

    return




if __name__ == "__main__":
    if len(sys.argv) == 4:
        axis = sys.argv[1]
        numPts_PH = sys.argv[2]
        numPts_TH = sys.argv[3]
        coordinateSearch(axis, numPts_PH, numPts_TH)
    elif len(sys.argv) == 8:
        axis=sys.argv[1]
        numPts_PH = sys.argv[2]
        numPts_TH = sys.argv[3]
        lb_PH=sys.argv[4]
        hb_PH=sys.argv[5]
        lb_TH=sys.argv[6]
        hb_TH=sys.argv[7]
        coordinateSearch(axis,)
    else:
        print("coordinateSearch.py NOT EXECUTED.  Incorrect number of arguments.  Correct usage is:")
        print("     ./coordinateSearch.py  [axis]  [numPts_PH]  [numPts_TH]       OR")
        print("     ./coordinateSearch.py  [axis]  [numPts_PH]  [numPts_TH]  [lb_PH]  [hb_PH]  [lb_TH]  [hb_TH]")
        sys.exit()