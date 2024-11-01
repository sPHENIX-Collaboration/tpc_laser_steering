#!/usr/bin/python3

import sys
import os
import time
from aimAt import aimAt

debug=False

def drawPattern():
    sleeptime=20
    axis=9N
    '''
    theta = [
        14.9326, 15.5004, 16.0818, 16.6745, 17.2767,
        15.1420, 17.4524, 15.4616, 17.7219, 15.9445,
        17.7212, 16.4252, 17.7341, 17.0702, 17.7232,
        18.9132, 18.3574, 19.1652, 18.9423, 19.5013,
        19.2207, 19.5889, 19.8054, 20.1864, 20.7377,
        21.1161, 21.7954, 22.8997, 21.4912, 22.3423,
        21.2201, 21.8029, 23.1986, 23.8134, 24.4268,
        23.5222, 23.8616, 24.2155, 25.0417, 24.4518,
        24.5829, 25.1477, 25.7132]

    phi = [
        241.892, 243.9, 245.757, 247.476, 249.07,
        241.005, 248.224, 239.722, 246.989, 239.52,
        245.349, 239.331, 243.71, 241.609, 232.461,
        229.537, 233.96, 231.875, 235.506, 233.997,
        234.74, 236.798, 236.189, 238.153, 225.834,
        227.649, 233.929, 231.48, 232.002, 230.194,
        229.992, 228.811, 221.886, 221.04, 220.241,
        223.559, 225.181, 226.75, 223.406, 224.269,
        228.268, 227.305, 226.39]
    #path={}
    #path['Dave']=[theta,phi]
    '''

    ''' 
    Seth's scan of how far in theta we can get:
    '''
    theta = [
        30, 35, 40, 45, 50,
        55, 60, 65, 70, 75,
        80]

    phi = [
        103, 108, 113, 118, 123,
        128, 133, 138, 143, 148,
        153]
        
    for i in range(theta.len()):
        aimAt(axis, axis, theta[i], phi[i])
        time.sleep(sleeptime)

    return




if __name__ == "__main__":    
    drawPattern()

