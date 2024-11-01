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

def coordinateSearch(axis, numPts_PH, numPts_TH, sleep=5, lb_PHI=None, hb_PHI=None, lb_THI=None, hb_THI=None):

    numPH=int(numPts_PH)
    numTH=int(numPts_TH)
    sleeptime=float(sleep)

    # TODO: make it so that we can use just 1 point
    if numPH<=1 or numTH<=1:
        return

    phiAxis = axis+"_PH"
    thsAxis = axis+"_TH_S"
    thlAxis = axis+"_TH_L"

    if lb_PHI == None:
        didChange = changeAxis(phiAxis)
        if not didChange:
            print("Could not get phi bounds")
            return
        lb_PH = 360*readback(ADDR['HARD_STOP1'])+1
    else:
        lb_PH=float(lb_PHI)
    
    if hb_PHI == None:
        hb_PH = 360*readback(ADDR['HARD_STOP2'])-1
    else:
        hb_PH = float(hb_PHI)
    
    if lb_THI == None:
        lb_TH = 10
    else:
        lb_TH = float(lb_THI)
    
    if hb_THI == None:
        hb_TH = 30
    else:
        hb_TH = float(hb_THI)

    phi_arr = [0.0]*numPH
    phi_space=(hb_PH-lb_PH)/(numPH-1)
    for i in range(numPH):
        phi_arr[i]=lb_PH+i*phi_space

    th_arr = [0.0]*numTH
    th_space=(hb_TH-lb_TH)/(numTH-1)
    for i in range(numTH):
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
    elif len(sys.argv) == 5:
        axis = sys.argv[1]
        numPts_PH = sys.argv[2]
        numPts_TH = sys.argv[3]
        sleep=sys.argv[4]
        coordinateSearch(axis, numPts_PH, numPts_TH, sleep)
    elif len(sys.argv) == 9:
        axis=sys.argv[1]
        numPts_PH = sys.argv[2]
        numPts_TH = sys.argv[3]
        sleep=sys.argv[4]
        lb_PH=sys.argv[5]
        hb_PH=sys.argv[6]
        lb_TH=sys.argv[7]
        hb_TH=sys.argv[8]
        coordinateSearch(axis,numPts_PH,numPts_TH,sleep,lb_PH,hb_PH,lb_TH,hb_TH)
    else:
        print("coordinateSearch.py NOT EXECUTED.  Incorrect number of arguments.  Correct usage is:")
        print("     ./coordinateSearch.py  [axis]  [numPts_PH]  [numPts_TH]            OR")
        print("     ./coordinateSearch.py  [axis]  [numPts_PH]  [numPts_TH]  [sleep]   OR")
        print("     ./coordinateSearch.py  [axis]  [numPts_PH]  [numPts_TH]  [sleep]  [lb_PH]  [hb_PH]  [lb_TH]  [hb_TH]")
        sys.exit()