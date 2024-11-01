#! /usr/bin/python3

import sys
import os
import time
from aimAt import aimAt
from goto import goto

sleeptime=5

def finalTest():

    aimAt("9N", "9N", 15, 113)
    for i in range(114, 203, 1):
        rev=i/360
        goto("9N_PH", rev)
        time.sleep(sleeptime)

    aimAt("9N", "9N", 25, 203)
    for i in range(202, 113, -1):
        rev=i/360
        goto("9N_PH", rev)
        time.sleep(sleeptime)

    return

if __name__ == "__main__":
    if len(sys.argv)==1:
        finalTest()
    else:
        sys.exit()