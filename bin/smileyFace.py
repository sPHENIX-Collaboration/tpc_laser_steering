#! /usr/bin/python3
#
# smileyFace.py draws a smiley face on the TPC central membrane

from quickReport import readback
from goto import goto
from changeAxisDogleg import changeAxis
from backAndForth import backAndForth
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
import sys
import time

lb_smile_9N = 0
hb_smile_9N = 0.25
eye1_9N = 
eye2_9N = 

def smileyFace(axis):

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
    if len(sys.argv) == 2:
        smileyFace()
    else:
        print("smileyFace.py NOT EXECUTED.  Correct usage is:")
        print("     ./smileyFace.py [axis]")
        sys.exit()