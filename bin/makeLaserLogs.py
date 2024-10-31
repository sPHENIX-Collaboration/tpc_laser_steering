#!/usr/bin/python3
import sys
import os
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varUniqueID as AXID

enr = 6.103515625e-5
pathPC = '/mnt/c/Users/smh28/Documents/Github/tpc_laser_steering/bin/axisLogs/'
path = '/home/pi/XCDCommandCodes/bin/axisLogs/'
suffix = '.log'

for axisName in AXID:
    print(axisName)
    filename = path + axisName + suffix
    with open(filename, "w") as file:

        file.write('{\"name\":\"%s\",\"USBport\":\"%s\"' % (axisName, "/dev/ttyUSB0"))
    
        for varName, varVal in ADDR.items():
            file.write(',\"%s\":%s' % (varName, 0.0))
        
        file.write('} \n')
