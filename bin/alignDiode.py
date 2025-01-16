#! /usr/bin/python3

import os
import sys
import time
import math
from quickReport import readback
from changeAxisDogleg import changeAxis
from gotoDogleg import gotoDogleg
from clearDogleg import clearDogleg

# SET DEFAULT GLOBAL VARIABLES
lb = -2.9   # low bound to travel to
hb = 2.9    # high bound to travel to
ss = 0.1    # step size to take in search
ns = 10     # numsteps to take
sleeptime = 

# set reset command - just run shell script
curl_pref = 'curl -o ./scopeTraces/st'
curl_suff = ' http://10.20.35.4:81/image.png'

def labelAxes(axis):

    # label axes to move from input axis
    DL0_A0 = axis + 'DL0_A0'
    DL0_A1 = axis + 'DL0_A1'
    DL1_A0 = axis + 'DL1_A0'
    DL1_A1 = axis + 'DL1_A1'

    return DL0_A0, DL0_A1, DL1_A0, DL1_A1


def takeImage(count, x_DL00, x_DL01, x_DL10, x_DL11):

    filename = str(count) + '_' + str(f"{x_DL00:.4f}") + '_' + str(f"{x_DL01:.4f}") + \
                '_' + str(f"{x_DL10:.4f}") + '_' + str(f"{x_DL11:.4f}") + '.png'
    img_save = curl_pref + filename + curl_suff
    os.system(img_save)
    count += 1

    return count


def wrapGoto(position, dummy=True):
    if dummy:
        print("gotoDogleg " + str(position))
        return True, position
    else:
        didGoto, pos = gotoDogleg(position)
        return didGoto, pos
    
def wrapChangeAxis(axis, dummy=True):
    if dummy:
        print("changeAxis " + str(axis))
        return True
    else:
        didChange = changeAxis(axis)
        return didChange


def moveAndCheck(move, axisName):

    # move DL0_A0 from spiral center to first step
    didGoto, pos = wrapGoto(move)
    if not didGoto:
        if pos == 0:
            print("findDiode move", axisName, " to ", pos, " failed.")
        else:
            x = input("gotoDogleg failed with above status. Press enter to clear or any other key then enter to abort.")
            if x != "":
                return False
            else:
                clearDogleg()
                return True

    return didGoto


def grid(axis):
    
    DL0_A0, DL0_A1, DL1_A0, DL1_A1 = labelAxes(axis)

    # start by moving chosen dogleg to (-2.9, 2.9)
    init_A0 = changeAxis(DL0_A0)
    goto_A0, pos0 = gotoDogleg(lb)
    init_A1 = changeAxis(DL0_A1)
    goto_A1, pos1 = gotoDogleg(lb)
    if not (init_A0 and goto_A0 and init_A1 and goto_A1):
        return

    # define initial moves
    move_A0 = hb
    move_A1 = lb + ss

    # 
    for i in range(ns):

        # change to DL0
        didChange_A0 = changeAxis(DL0_A0)
        if not didChange_A0:
            print("findDiode change to A0 failed on step ", i)
            return

        # move A0 from to either lb or hb
        didGoto_A0, pos0 = gotoDogleg(move_A0)
        if not didGoto_A0:
            if pos0 == 0:
                print("findDiode A0 move step ", i, " to ", pos0, " failed.")
                return
            else:
                x = input("gotoDogleg failed with above status. Press enter to clear or any other key then enter to abort.")
                if x != "":
                    return
                else:
                    clearDogleg()


        # change to DL1
        didChange_A1 = changeAxis(DL0_A1)
        if not didChange_A1:
            print("findDiode change to A1 failed on step ", i)
            return

        # move A1 up by step size ss
        didGoto_A1, pos1 = gotoDogleg(move_A1)
        if not didGoto_A1:
            if pos1 == 0:
                print("findDiode A1 move step ", i, " to ", pos1, " failed.")
                return
            else:
                x = input("gotoDogleg failed with above status. Press enter to clear or any other key then enter to abort.")
                if x != "":
                    return
                else:
                    clearDogleg()


        x = input("Press enter to perform next move.  Press any key then enter to abort.")
        if x != "":
            return
        else:
            move_A0 = -1*move_A0
            move_A1 = move_A1 + ss

    print("findDiode:gridSearch finished.")

    return


def spiral(axis, x_DL00:float=0.0, x_DL01:float=0.0, x_DL10:float=0.0, x_DL11:float=0.0, ns0:int=ns, \
            ns1:int=ns, step_size:int=ss, autorun:bool=True, img_bool:bool=True):

    DL0_A0, DL0_A1, DL1_A0, DL1_A1 = labelAxes(axis)

    # start by moving first dogleg to (x_DL00,x_DL01), default (0,0)
    init_DL00 = wrapChangeAxis(DL0_A0)
    goto_DL00, pos00 = wrapGoto(x_DL00)
    init_DL01 = wrapChangeAxis(DL0_A1)
    goto_DL01, pos01 = wrapGoto(x_DL01)
    if not (init_DL00 and goto_DL00 and init_DL01 and goto_DL01):
        return
    
    # start by moving chosen dogleg to (x_DL10,x_DL11), default (0,0)
    init_DL10 = wrapChangeAxis(DL1_A0)
    goto_DL10, pos10 = wrapGoto(x_DL10)
    init_DL11 = wrapChangeAxis(DL1_A1)
    goto_DL11, pos11 = wrapGoto(x_DL11)
    if not (init_DL10 and goto_DL10 and init_DL11 and goto_DL11):
        return

    # save first image
    count:int = 0
    count = takeImage(count, x_DL00, x_DL01, x_DL10, x_DL11) 
    
    # calculate initial moves
    innerstep = -1*step_size
    outerstep = -1*step_size
    mv_DL00 = x_DL00
    mv_DL01 = x_DL01
    mv_DL10 = x_DL10
    mv_DL11 = x_DL11

    # spiral for upstream dogleg DL0
    for i in range(ns0):
        # change to DL0_A0, return if failed
        didChange_DL00 = wrapChangeAxis(DL0_A0)
        if not didChange_DL00:
            print("findDiode:spiralSearch change to DL0_A0 failed on step ", i)
            return
        
        for ii in range(i+1):
            # increase (or decrease) move by one step
            mv_DL00 = mv_DL00 + outerstep
            # move DL0_A0 from spiral center to first step
            if not moveAndCheck(mv_DL00, DL0_A0):
                return
            # take picture if we want pics
            if img_bool:
                count = takeImage(count, mv_DL00, mv_DL01, mv_DL10, mv_DL11)
            # stop in between each move if autorun not turned on
            if not autorun:
                x = input("Press enter to perform next move.  Press any key then enter to abort.")
                if x != "":
                    return


            # spiral for downstream dogleg DL1
            for j in range(ns1):
                # change to DL1_A0
                didChange_DL10 = wrapChangeAxis(DL1_A0)
                if not didChange_DL10:
                    print("findDiode:spiralSearch change to DL1_A0 failed on step ", i)
                    return
                
                for jj in range(j+1):
                    # increase (or decrease) move by one step
                    mv_DL10 = mv_DL10 + innerstep
                    # move DL1_A0 to new move
                    if not moveAndCheck(mv_DL10, DL1_A0):
                        return
                    didGoto_DL10, pos10 = wrapGoto(mv_DL10)
                    # take picture if we want pics
                    if img_bool:
                        count = takeImage(count, mv_DL00, mv_DL01, mv_DL10, mv_DL11)
                    # stop in between each move if autorun not turned on
                    if not autorun:
                        x = input("Press enter to perform next move.  Press any key then enter to abort.")
                        if x != "":
                            return

                # change to DL1_A1
                didChange_DL11 = wrapChangeAxis(DL1_A1)
                if not didChange_DL11:
                    print("findDiode change to DL1_A1 failed on step ", j)
                    return
                
                for jj in range(j+1):
                    # increase (or decrease) move by one step
                    mv_DL11 = mv_DL11 + innerstep
                    # move A1 up by step size ss
                    if not moveAndCheck(mv_DL11, DL1_A1):
                        return
                    # take picture if we want pics
                    if img_bool:
                        count = takeImage(count, mv_DL00, mv_DL01, mv_DL10, mv_DL11)
                    # stop in between each move if autorun not turned on
                    if not autorun:
                        x = input("Press enter to perform next move.  Press any key then enter to abort.")
                        if x != "":
                            return

                innerstep = -1*innerstep

        # change to DL0_A1, return if failed
        didChange_DL01 = wrapChangeAxis(DL0_A1)
        if not didChange_DL01:
            print("findDiode change to DL0_A1 failed on step ", i)
            return
        
        for ii in range(i+1):
            # increase (or decrease) move by one step
            mv_DL01 = mv_DL01 + outerstep
            # move A1 up by step size ss
            if not moveAndCheck(mv_DL01, DL0_A1):
                return
            # take picture if we want pics
            if img_bool:
                count = takeImage(count, mv_DL00, mv_DL01, mv_DL10, mv_DL11)
            # stop in between each move if autorun not turned on
            if not autorun:
                x = input("Press enter to perform next move.  Press any key then enter to abort.")
                if x != "":
                    return

            # spiral for downstream dogleg DL1
            for j in range(ns1):

                # change to DL1_A0
                didChange_DL10 = wrapChangeAxis(DL1_A0)
                if not didChange_DL10:
                    print("findDiode:spiralSearch change to DL1_A0 failed on step ", i)
                    return
                for jj in range(j+1):
                    # increase (or decrease) move by one step
                    mv_DL10 = mv_DL10 + innerstep
                    # move DL1_A0 to 
                    if not moveAndCheck(mv_DL10, DL1_A0):
                        return
                    # take picture if we want pics
                    if img_bool:
                        count = takeImage(count, mv_DL00, mv_DL01, mv_DL10, mv_DL11)
                    # stop in between each move if autorun not turned on
                    if not autorun:
                        x = input("Press enter to perform next move.  Press any key then enter to abort.")
                        if x != "":
                            return
                    

                # change to DL1_A1
                didChange_DL11 = wrapChangeAxis(DL1_A1)
                if not didChange_DL11:
                    print("findDiode change to DL1_A1 failed on step ", j)
                    return
                for jj in range(j+1):
                    # increase (or decrease) move by one step
                    mv_DL11 = mv_DL11 + innerstep
                    # move A1 up by step size ss
                    if not moveAndCheck(mv_DL11, DL1_A1):
                        return
                    # take picture if we want pics
                    if img_bool:
                        count = takeImage(count, mv_DL00, mv_DL01, mv_DL10, mv_DL11)
                    # stop in between each move if autorun not turned on
                    if not autorun:
                        x = input("Press enter to perform next move.  Press any key then enter to abort.")
                        if x != "":
                            return

                innerstep = -1*innerstep

        outerstep = -1*outerstep

    print('findDiode:spiralSearch completed.')

    return


# Convert hyperspherical coordinates to Cartesian coordinates
def fourSphere2Cartesian(r, theta1, theta2, theta3):
    """
    Convert hyperspherical coordinates to Cartesian coordinates.

    r: Radius of the 4-sphere
    theta1, theta2, theta3: Angular coordinates (in radians)

    Returns: (x, y, z, w)
    """
    x = r * math.sin(theta1) * math.sin(theta2) * math.sin(theta3)
    y = r * math.sin(theta1) * math.sin(theta2) * math.cos(theta3)
    z = r * math.sin(theta1) * math.cos(theta2)
    w = r * math.cos(theta1)
    return x, y, z, w



def fourSphere(axis, radius, numPts=30):
    """
    Scan for diode across successively larger 4D hyperspheres.
    """
    # create dogleg axis names from given axis
    DL0_A0, DL0_A1, DL1_A0, DL1_A1 = labelAxes(axis)

    # for fourSphere search, initialize 
    theta1_vals = [math.pi*res*i for i in range(numPts)]        # first angle
    theta2_vals = [math.pi*res*i for i in range(numPts)]        # second angle
    theta3_vals = [2*math.pi*res*i for i in range(numPts)]      # third angle

    # Iterate through all combinations of angles
    # r^2 = x1^2 + x2^2 + x3^2 + x4^2
    # for a given r^2, start at x1 = r, x2=x3=x4=0
    # x00, x01, x10, x11 = fourSphere2Cartesian(radius, theta1, theta2, theta3)
    for r in radius:
        # calculate resolution of points on 4d sphere surface 
        res = 1/(radius*(numPts-1))

        for theta1 in theta1_vals:

            x00 = r * math.cos(theta1)
            if not wrapChangeAxis(DL0_A0):
                print("findDiode:fourSphere change to DL0_A0 failed")
                return
            movebool = moveAndCheck(x00)

            for theta2 in theta2_vals:

                x01 = r * math.sin(theta1) * math.cos(theta2)
                if not wrapChangeAxis(DL0_A1):
                    print("findDiode:fourSphere change to DL0_A0 failed")
                    return
                movebool = moveAndCheck(x01)

                for theta3 in theta3_vals:
                    
                    # convert to Cartesian for 
                    x10 = r * math.sin(theta1) * math.sin(theta2) * math.sin(theta3)
                    x11 = r * math.sin(theta1) * math.sin(theta2) * math.cos(theta3)

                    
                    if not wrapChangeAxis(DL1_A0):
                        print("findDiode:fourSphere change to DL1_A0 failed")
                        return
                    movebool = moveAndCheck(x10)
                    
                    if not wrapChangeAxis(DL1_A1):
                        print("findDiode:fourSphere change to DL1_A1 failed")
                        return
                    movebool = moveAndCheck(x11)

                    if sleeptime != 0:
                        time.sleep(sleeptime)

                    # TODO: add modular pause
                    # TODO: for laserLog, how to signal that laser is stopped
                    # TODO: figure how many steps, degree to which they are bunched up (calculate Cartesian distance between coords, create histogram)
                    # TODO: integrate pmonitor script
    
    return


'''
alignDiode
rig to spit out csv of diodes
check versus granularity of inner mirrors to see how many steps/how long it takes

how to prevent recording motor positions while moving
brainstorm signals in laserLog that laser is moving or stopped

write file "IhaveStopped"
as long as file exists, writing to laserLog can happen

create histogram that samples

'''

if __name__ == "__main__":
    #check args
    if len(sys.argv) == 2:
        axis = sys.argv[1]
        spiral(axis)
    elif len(sys.argv) == 11:
        axis, x_DL00, x_DL01, x_DL10, x_DL11, ns0, ns1, step_size, autorun, img_bool = sys.argv[1:11]
        try:
            x_DL0_A0 = float(x_DL00)
            x_DL0_A1 = float(x_DL01)
            x_DL1_A0 = float(x_DL10)
            x_DL1_A1 = float(x_DL11)
            nums0 = int(ns0)
            nums1 = int(ns1)
            steps = int(step_size)
        except ValueError:
            sys.exit()
        spiral(axis, x_DL0_A0, x_DL0_A1, x_DL1_A0, x_DL1_A1, nums0, nums1, steps, autorun, img_bool)
    else:
        print("alignDiode.py incorrect number of arguments.  Correct usage is:")
        print("     ./alignDiode.py  axis  xi_DL0A0  xi_DL0A1  xi_DL1A0  xi_DL1A1  #stepsDL0  #stepsDL1  stepsize")
        sys.exit()