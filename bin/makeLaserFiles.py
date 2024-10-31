#! /usr/bin/python3
import sys
import os
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varUniqueID as AXID

for axisName in AXID:
    with open(os.path.join('/home/pi/XCDCommandCodes/bin/laserFiles', axisName), "w") as file:

        for varName, varVal in ADDR.items():
            enr = 6.103515625e-5
            axis = 0
            if (AXID[axisName] % 2) == 0:
                axis = 1
            
            if varName == 'ID':
                file.write('ID %s\n' % AXID[axisName])
            elif varName == 'XAXIS':
                file.write('XAXIS %s\n' % axis)
            elif varName == 'ENR':
                file.write('ENR %s\n' % enr)
            else:
                file.write('%s %s\n' % (varName, 0.0))