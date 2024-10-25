#! /usr/bin/python3
#
# smileyFace.py draws a smiley face on the TPC central membrane

from quickReport import readback
from goto import goto
from changeAxisDogleg import changeAxis
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
import sys

def draw(axis, range, duration):

    

    return


def smileyFace(axis):


    return


if __name__ == "__main__":
    if len(sys.argv) == 2:
        smileyFace()
    else:
        print("smileyFace.py NOT EXECUTED.  Correct usage is:")
        print("     ./smileyFace.py [axis]")
        sys.exit()