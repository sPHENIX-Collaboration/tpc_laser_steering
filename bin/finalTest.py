#! /usr/bin/python3

import sys
import os
from aimAt import aimAt
from goto import goto


def finalTest():

    aimAt("9N", "9N", 15, 113)
    for i in range(114, 203, 1):
        rev=i/360
        goto("9N_PH", rev)

    aimAt("9N", "9N", 25, 203)
    for i in range(202, 113, -1):
        rev=i/360
        goto("9N_PH", rev)

    return

if __name__ == "__main__":
    if len(sys.argv)==1:
        finalTest()
    else:
        sys.exit()