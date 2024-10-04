#! /usr/bin/python3

import os
import sys
import time
import math
from quickReport import readback, reportXCD2
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from goto import goto

# to load axis data from the db:
sys.path.append("kfDatabase")
import kfDatabase

# tuning settings
sleeptime=0.5 #in seconds
debug=False
mainDb = 'axis_parameters.kfdb'


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def setLight( attenuator=None, inputval=None, openloop=False):

    if attenuator==None or inputval==None:
        print("wrong args for setLight.  requires two arguments.")
        return False

    # convert attenuator percentage from str to float
    try:
        percentage = float(inputval)
    except ValueError:
        print("Error: Not a valid number")
        return False, 0
    
    # find minlight and maxlight positions from database
    minKey = attenuator+"/minlight"
    maxKey = attenuator+"/maxlight"
    # get the value from the dict.
    if debug:
        print("setLight: looking for attenuator min/max values %s , %s"% (minKey, maxKey))
    minPos = -1000
    maxPos = -1000
    maxBool,maxPos=kfDatabase.readVar(mainDb, maxKey)
    minBool,minPos=kfDatabase.readVar(mainDb, minKey)
    # check that it returned successfully
    if not (minBool or maxBool):
        print("setLight: kfDatabase failed.  minLight '%s' or maxLight '%s' (or both) not found. (kfdb=%s, , minKey=%s, maxKey=%s)" % (minPos,maxPos,mainDb,minKey,maxKey))
        return False        
    #  check to see if the dict value is a number.
    #  if number: make it a float.
    if (is_number(minPos)):
        targetPos=float(minPos ) 
    else:
        print("setLight: kfDatabase key '%s' has non-numeric value %s" % (maxKey,str(minPos)))
        return False



    # we presume the attenuator has a sin^2() profile
    #fractional position between low and high is:
    #light_percentage=sin^2(pi/2*(pos-minpos)/(maxpos-minpos)) (we get a peak whenever our linear fraction is an odd integer)
    #sqrt(light_percentage)=sin(pi/2 * linear_fraction)
    #pi/2*linear_fraction=asin(sqrt(light_percentage)
    linear_fraction = 2/math.pi*(math.asin(math.sqrt(percentage)))
    #the desired position is the minlight position plus that fraction of the distance between min and max
    #linear_fraction=(desired_pos-minpos)/(maxpos-minpos)
    #this has the advantage of taking care of any directionality (max>min or max<min) automatically.
    desired_pos=minPos+(maxPos-minPos)*linear_fraction
    print("setLight: desired_pos=%s+(%s-%s)*%s=%s.  Driving %s to %s. (kfdb=%s, minKey=%s, maxKey=%s, pct=%s)" % (minPos,maxPos,minPos,linear_fraction,desired_pos, attenuator,desired_pos, mainDb,minKey,maxKey,percentage))
    goto(attenuator,desired_pos,openloop)
    
    return



if __name__ == "__main__":
    #check args
    if len(sys.argv)==3:
        #keep current leg, assume arg is destination.
        attenuator=sys.argv[1]
        inputval = sys.argv[2]
        openloop=False
    elif len(sys.argv)==4:
        if sys.argv[3] != "ol":
            print("NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
            print("     ./setLight.py 9N_AT [position]")
            print("     ./setLight.py 9N_AT [position] ol")
            sys.exit()
        attenuator=sys.argv[1]
        inputval = sys.argv[2]
        openloop=True
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is:")
        print("     ./setLight.py 9N_AT [position]")
        print("     ./setLight.py 9N_AT [position] ol")
        sys.exit()
 
    setLight( attenuator, inputval,openloop )
    #if wrong arguments, exit with explanation
