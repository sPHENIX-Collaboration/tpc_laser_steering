#!/usr/bin/python3

import sys
import os
import time
from aimAt import aimAt
from patternDictionary import points

debug=False

def drawPattern(pattern=None):
    sleeptime=20
    axis='9N'
    if not pattern:
        return
    pair=points.get(pattern)
    if not pair:
        print("%s not found in pattern dictionary. available patterns:"%pattern)
        for key in points.keys():
            print(key)
        return
    
    theta=pair['theta']
    phi=pair['phi']
 
        
    for i in range(len(theta)):
        aimAt(axis, axis, theta[i], phi[i])
        #print("aimAt(%s,%s,%s,%s)"%(axis,axis,theta[i],phi[i]))
        time.sleep(sleeptime)

    return




if __name__ == "__main__":    
    drawPattern(sys.argv[1])

