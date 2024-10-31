#!/usr/bin/python3
import sys
import os
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varUniqueID as AXID

enr = 6.103515625e-5
path = '/home/pi/XCDCommandCodes/bin/axisLogs/'
suffix = '.log'

for axisName in AXID:
    print(axisName)
    filename = path + axisName + suffix
    with open(filename, "w") as file:

        file.write('{\"name\":%s' % (axisName))
    
        for varName, varVal in ADDR.items():
            file.write(',\"%s\":%s' % (varName, 0.0))
        
        file.write('} \n')
