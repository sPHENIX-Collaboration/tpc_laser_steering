#!/usr/bin/python3

# This is designed to tell a particular egg to steer to a given (x,y) coordinate pair on the central membrane

from aimAt import aimAt
import sys
import math
    


def aimAtCentralMembrane(laserName, x=0,y=0):
    x=float(x)
    y=float(y)
    z=0
    #assume we have phi and theta in degrees
    xo=-510
    yo=160
    zo=1050

    #theta angle is the triangle in the phi direction, so 
    base=math.sqrt((x-xo)**2+(y-yo)**2)
    height=zo-z
    theta=atan(base/height)

    #phi angle is the target phi:
    horiz=(x-xo)
    vert=(y-yo)
    phi=atan2(vert,horiz)

    aimAt(laserName, laserName, theta, phi+180)
    return






if __name__ == "__main__":
    #check args
    if len(sys.argv)==4:
        #assume (eggDbName,theta,phi).
        #TODO:  specify which laser (port,axis), and which egg?  Or should we mate those permanently in the db?
        #get its port from the db
        laserName=sys.argv[1]
        x=sys.argv[2]
        y=sys.argv[3]
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("   ./aimAtCentralMembrane.py [axis] [x] [y]")
        sys.exit()
    #if wrong arguments, exit with explanation

    aimAtCentralMembrane(laserName,x,y)
