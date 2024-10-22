#! /usr/bin/python3
#
# for a given pair of thetas
# can input desired position
# if already at desired starting position, don't enter in values
# start by moving theta long to edge ()

import sys
from quickReport import readback
from goto import goto
from changeAxisDogleg import changeAxis
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR


def inchworm(axis, THS_start=None, THL_start=None):

    # define reasonable step sizes (fraction of full range) based on geometry of theta mirrors 
    # THL displaced from rotation axis by 5.5-6mm (from Dan/Kristina), 3mm mirror width and 1mm beam spot
    # to keep beam fully on mirror for each step, use 2mm step size, s=r*TH --> THL=0.33deg=0.006 rotations
    # maximum THL step size moves beam spot off mirror (4mm --> THL=0.66deg=0.012 rotations)
    THL_step=0.006
    THS_step=-0.003
    inch="y"

    axisTHS = axis + "_TH_S"
    axisTHL = axis + "_TH_L"

    # if no values input, readback current stored position
    if THS_start==None or THL_start==None:
        changeAxis(axisTHS)
        pos_THS = readback(ADDR['FPOS'])
        changeAxis(axisTHL)
        pos_THL = readback(ADDR['FPOS'])
    
    # otherwise move to desired starting position (for THS and THL)
    else:
        changeAxis(axisTHS)
        goto(THS_start)
        pos_THS = readback(ADDR['FPOS'])
        changeAxis(axisTHL)
        goto(THL_start)
        pos_THL = readback(ADDR['FPOS'])


    # inch positive or negative?
    x = input("Choose a move direction: 'p' for positive and 'n' for negative")
    if x == 'n':
        THL_step = -1*THL_step
        THS_step = -1*THS_step

    # first move THL half step to get to edge (uses THS_step value since it is half)
    s_i, pos_i = goto(pos_THL - THS_step)

    # then start looping through alternating THS and THL moves
    while inch=="y":

        move_THS, pos_THS = goto(pos_THS + THS_step)
        if not move_THS:
            x = input("Try again? If no, program will exit. [y/n]")
            if x=="n":
                return
        
        move_THL, pos_THL = goto(pos_THL + THL_step)
        if not move_THL:
            x = input("Try again? If no, program will exit. [y/n]")
            if x=="n":
                return
        
        x = input("Perform another inch? [y/n]")
        inch = x
    
    return


if __name__ == "__main__":
    if len(sys.argv) == 3:
        THS_i=sys.argv[1]
        THL_i=sys.argv[2]
        inchworm(THS_i, THL_i)
    elif len(sys.argv) == 1:
        inchworm()
    else:
        print("wiggleAxis.py failed.  Incorrect number of arguments.")
        sys.exit()