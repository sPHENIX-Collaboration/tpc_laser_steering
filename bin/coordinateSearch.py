#!/usr/bin/python3

import sys
import os
from quickAssign import writeXCD2
from quickReport import reportXCD2
from backAndForth import backAndForth
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR

def coordinateSearch(axis, lb_PH=None, hb_PH=None, step_PH, lb_TH=None, hb_TH=None, step_TH):

    phiAxis = axis+"_PH"
    thsAxis = axis+"_TH_S"
    thlAxis = axis+"_TH_L"

    didChange = changeAxis()
    backAndForth(phiAxis, )
    didChange = changeAxis()
    goto()
    backAndForth(thsAxis)

    return

if __name__ == "__main__":
    if len(sys.argv) == 