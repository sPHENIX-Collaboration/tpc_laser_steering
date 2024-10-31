#!/usr/bin/python3

# This is designed to tell a particular egg to draw a series of line segments to spell words on the CM

from aimAtCentralMembrane import aimAtCentralMembrane
import sys
import math
import time

    


def drawWords(laserName,t=1,steps=20):
    #t is the wait time in seconds.

    
    Dave={'start':[
        (0, 0), (0, 2), (0.5, 2), (1, 1.6),
        (1, 0.4), (0.5, 0), (1.5, 0), (2, 2),
        (2, 2), (2.5, 0), (1.75, 1), (2.25, 1),
        (2.5, 2), (3, 0), (3, 0), (3.5, 2),
        (4, 2), (4, 0), (4, 0), (5, 0),
        (5, 1), (4, 1), (5, 2), (4, 2)
        ],
        'end':[
        (0, 2), (0.5, 2), (1, 1.6), (1, 0.4),
        (0.5, 0), (0, 0), (2, 2), (2.5, 0),
        (1.75, 1), (2.25, 1), (3, 0), (3.5, 2),
        (4, 0), (5, 0), (4, 1), (5, 1),
        (4, 2), (4, 2), (5, 2), (5, 2)
        ]
        }
    #add offset, add scale
    scale=100
    shift=(-400,300)
    #todo:  add rotation offset?
    #todo:  make steps have a target stepsize instead of fixed number
    for s0,e0 in zip(Dave['start'],Dave['end']):
        sx=s0[0]*scale+shift[0]
        sy=s0[1]*scale+shift[1]
        ex=e0[0]*scale+shift[0]
        ey=e0[1]*scale+shift[1]
        step = ((ex - sx)/steps, (ey - sy)/steps)
        for i in range(steps):
            aimAtCentralMembrane(laserName, sx+step[0]*i, sy+step[1]*i)
            time.sleep(t)
    return
  





if __name__ == "__main__":
    #check args
    if len(sys.argv)==4:
        laserName=sys.argv[1]
        t=sys.argv[2]
        steps=sys.argv[3]
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("   ./drawWords.py [axis] [t] [steps]")
        sys.exit()
    #if wrong arguments, exit with explanation

    drawWords(laserName,t,steps)
