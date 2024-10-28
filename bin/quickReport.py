#!/usr/bin/python3
import time
from xcdSerial import sendline, getCurrentPort
from variableDictionaryXCD2 import varDict
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
import sys
import struct

debug=False

def readback(arg):
    #returns the value using the controller variable naming scheme
    check,ret = reportXCD2([arg])
    if check==False:
        print("CRITICAL FAILURE. Communication error.")
        sys.exit()
    if debug:
        print("_readback result: ", ret[0])
    return ret[0]


def getAxis():
    stat,ret =reportXCD2noAxis(['XAXIS'])
    if not stat:
        print("Could not getAxis()")
        sys.exit()
    return int(ret[0])

def reportXCD2( argv ):#by default, we ask for the variables from the current active axis.
    ax_int = getAxis()
    if debug:
        print("passing through from reportXCD2 to reportXCDspecifyAxis(%s,%s)"%(ax_int,argv))
    success,ret = reportXCD2specifyAxis(ax_int,argv)
    return success,ret
 


def reportXCD2specifyAxis(axis, argv ):
    if argv:
        if len(argv) > 10:
            print("reportXCD2specifyAxis: Too many variables trying to be requested.  Max 10 variables can be assigned at once.")
            return False, 0

        var_names = argv
        if debug:
            print(var_names)
        
        #getAxis = reportXCD2noAxis(['XAXIS'])[0]

        ax_int = axis
        ax_byte = ax_int.to_bytes(1,byteorder='little',signed=True)
        ax_comm = [int(ax_byte[0])]
        
        command = [228, 165, 0, 213, 0, 0, 6, 132]
        count = 0
        for i in range(0, len(var_names)):
            var = var_names[i]


            if var in varDict.keys():
                var_num = varDict[var]
                u2 = var_num.to_bytes(2,byteorder='little',signed=False)
                var_command = [int(u2[0]), int(u2[1])]
                command += var_command
                count += 2
            else:
                print("Variable name - ", var , " -  not recognized. Variable list given as:")
                print(varDict.keys())
                return False, 0
            
            command += ax_comm
            count += 1

    else:
        print("No arguments given. reportXCD2 parameters are: \n \
               1) Variable- Mandatory, variable to report value of. For full list of variables, refer to variableDictionary. \n \
               2-10) Variable - Optional, other variables to report. \
               ")
        return False, 0

    # reassign packet length and block length bytes
    command[4] = int(count+6)
    command[5] = int(count+3)
    # add stop byte
    command += [218]
    if debug:
        print(command)

    # the next portion of code is what establishes communication with the controller
    # and sends the bytestring command by serial comm
    # and returns a pair of [succeeded,readbackline]
    success,ret=sendline(getCurrentPort(),command)
    if success and debug:
        print(ret)
    return success, ret

def reportXCD2noAxis( argv ): #reports the requested argument list using the current port, and without specifying an axis  (hence using current axis)
    return reportXCD2noAxisPort(getCurrentPort(),argv)

def reportXCD2noAxisPort(target_port, argv ): #reports the requested argument list from the requested port, without specifying an axis (hence using current axis)
    if argv:
        if len(argv) > 10:
            print("Too many variables trying to be requested.  Max 10 variables can be requested at once.")
            return False, 0

        var_names = argv
        if debug:
            print(var_names)

        command = [228, 165, 0, 213, 0, 0, 6, 4]
        count = 0
        for i in range(0, len(var_names)):
            var = var_names[i]

            if var in varDict.keys():
                var_num = varDict[var]
                u2 = var_num.to_bytes(2,byteorder='little',signed=False)
                var_command = [int(u2[0]), int(u2[1])]
                command += var_command
                count += 2
            else:
                print("Variable name - " , var , " -  not recognized. Variable list given as:")
                print(varDict.keys())
                return False, 0

    else:
        print("No arguments given. reportXCD2 parameters are: \n \
               1) Variable- Mandatory, variable to report value of. For full list of variables, refer to variableDictionary. \n \
               2-10) Variable - Optional, other variables to report. \
               ")
        return False, 0

    # reassign packet length and block length bytes
    command[4] = int(count+6)
    command[5] = int(count+3)
    # add stop byte
    command += [218]
    if debug:
        print(command) 

    # the next portion of code is what establishes communication with the controller
    # and sends the bytestring command by serial comm
    success,ret=sendline(target_port,command)
    if success and debug:
        print(ret)
    return success, ret


if __name__ == "__main__":
    debug=True
    reportXCD2(sys.argv[1:])
