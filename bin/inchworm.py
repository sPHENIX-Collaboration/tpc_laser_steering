#! /usr/bin/python3
#
# for a given pair of thetas
# can input desired position
# if already at desired starting position, don't enter in values
# start by moving theta long to edge ()

import sys
from quickReport import readback
from goto import goto
from aimAt import aimAt, getThetaMotorCoordinates
from changeAxisDogleg import changeAxis
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR


def inchworm(axis, finalAngle=None, startAngle=None, quiet=False):

    # define reasonable step sizes (fraction of full range) based on geometry of theta mirrors 
    # THL displaced from rotation axis by 5.5-6mm (from Dan/Kristina), 3mm mirror width and 1mm beam spot
    # to keep beam fully on mirror, maximum range is 2mm, s=r*TH --> THL=0.33rad=0.053 rotations
    # maximum THL step size moves is half this, so we use 0.02 rotations to be conservative
    THL_step=0.02
    THS_step=-THL_step/2
    inch="y"

    axisTHS = axis + "_TH_S"
    axisTHL = axis + "_TH_L"

    # if no values input, readback current stored position
    if startAngle==None:
        changeAxis(axisTHS)
        pos_THS = readback(ADDR['FPOS'])
        changeAxis(axisTHL)
        pos_THL = readback(ADDR['FPOS'])
    
    # otherwise move to desired starting position (for THS and THL)
    else:
        THS_start, THL_start = getThetaMotorCoordinates(axis, startAngle)
        sTHS, pos_THS = goto(axisTHS, THS_start)
        sTHL, pos_THL = goto(axisTHL, THL_start)
        if (sTHS != True) or (sTHL != True):
            print("inchworm.py did not arrive at starting angle.  Try changing parameters then run again.")
            return

    # handles single inch case for now, need to figure out what one inch corresponds to
    if finalAngle==None:
        return

    # determine number of inchworm steps to make by using THL step size (easier to control than THS)
    # and also determine direction of travel from 
    THS_end, THL_end = getThetaMotorCoordinates(axis, finalAngle)
    dirTravel = THL_end - THS_end
    numSteps = int(abs((dirTravel)/THL_step))
    if dirTravel < 0:
        THL_step = -1*THL_step
        THS_step = -1*THS_step
    
    # first move THL half step to get to edge (uses THS_step value since it is half)
    # s_i, pos_i = goto(pos_THL - THS_step)

    # calculate the different theta angles corresponding to inchworm steps
    arrTheta = [0.0]*numSteps
    for i in range(0, numSteps, 1):
        arrTheta[i] = startAngle + (finalAngle - startAngle)/numSteps


    # then start looping through theta moves using aimAt
    n = 0
    while inch=="y" and numSteps>0:

        # take theta2 - theta1/step size gives number of steps
        # at each step aimAt theta for that step
        aimAt(axis, axis, theta=arrTheta[n])


        # move_THS, pos_THS = goto(axisTHS, pos_THS + THS_step)
        # if move_THS:
        #     print("inchworm.py THS arrived at ", pos_THS, " .")
        # else:
        #     x = input("inchworm.py THS failed to arrive. Try again? If no, program will exit. [y/n]: ")
        #     if x=="n":
        #         return
        # move_THL, pos_THL = goto(axisTHL, pos_THL + THL_step)
        # if move_THL:
        #     print("inchworm.py THS arrived at ", pos_THL, " .")
        # else:
        #     x = input("inchworm.py THL failed to arrive. Try again? If no, program will exit. [y/n]: ")
        #     if x=="n":
        #         return
        
        x = input("Perform another inch? [y/n]: ")
        inch = x
        n += 1

    return



if __name__ == "__main__":
    if len(sys.argv) == 4:
        axis=sys.argv[1]
        final=sys.argv[2]
        initial=sys.argv[3]
        inchworm(axis, final, initial)
    elif len(sys.argv) == 3:
        axis=sys.argv[1]
        final=sys.argv[2]
        inchworm(axis, final)
    elif len(sys.argv) == 2:
        axis=sys.argv[1]
        inchworm(axis)        
    else:
        print("wiggleAxis.py failed.  Incorrect number of arguments.")
        sys.exit()