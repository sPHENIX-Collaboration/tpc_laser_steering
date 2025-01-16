#! /usr/bin/python3
#
#  xcdMotor.py
#
#  Created by Seth Howell on 2/3/24.
#  Copyright © 2024. All rights reserved.

import os
import sys
import re
import struct
import time

sys.path.append("C:/Users/smh28/Documents/Github/tpc_laser_steering/bin/")
import xcdSerial
import variableDictionaryXCD2
from variableDictionaryXCD2 import varAllCommands as ALL_COMM 
from variableDictionaryXCD2 import varStatusValues as STAT
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR


debug = False
portsDatabase = "xcd2_ports.kfdb"


# startup idea:
# updatePorts whenever plugging something in or unplugging it (including power cycles).
#    that creates a file with lines arranged:  laser portname axis
# homeEggs
# homePhi for all phis we find
# homeThetaS for all thetaS
# homeThetaL for all thetaL




############################################################
# COMMUNICATION SCRIPTS - not directly tied to a given class
############################################################

def readback(arg):
    #returns the value using the controller variable naming scheme
    check,ret = reportXCD2([arg])
    if check==False:
        print("CRITICAL FAILURE. Communication error.")
        sys.exit()
    if debug:
        print("_readback result: ", ret[0])
    return ret[0]



def sendcommand(com,arg):
    if debug:
        print("command:  Check status:")
    status=readback(ADDR['STATUS'])
    if status!=STAT['READY']:
        print("NOT EXECUTED.  Error: sendcommand: Controller is not in ready state.  Status=",status)
        return False
        #instead of sys.exit()
    try:
        input = float(arg)
    except ValueError:
        print("NOT EXECUTED.  Error: Not a valid number, arg=",arg)
        return False
        #instead of sys.exit()

    if debug:
        print("sendcommand: set argument:")    
    writeXCD2([ADDR['ARG'], arg])    
    if debug:
        print("sendcommand: set status to new_command:")    
    writeXCD2([ADDR['STATUS'], STAT['NEWCOMMAND']])
    #set the command byte last, so we know we don't have a race condition
    if debug:
        print("sendcommand: set command byte:")    
    writeXCD2([ADDR['COMMAND'],com])

    #now wait until the status changes to indicate the command has been acted on:
    if debug:
        print ("sendcommand: priming status check be ore wait")
    status=readback(ADDR['STATUS'])
    print("sendcommand says status is ",status," (",_reverseLookup(STAT,status),").")
    t1=time.time()
    timedOut=False
    while status==STAT['NEWCOMMAND'] and (not timedOut):
        if (time.time()-t1) > timeout:
            print("sendcommand:  command timed out.  No response from controller")
            writeXCD2([ADDR['COMMAND'],0.0])
            writeXCD2([ADDR['STATUS'],STAT['FAIL_DID_NOT_RESPOND']])
            
            timedOut=True
        if debug:
            print ("sendcommand: waiting for device to ack command:")
        status=readback(ADDR['STATUS'])
        time.sleep(sleeptime)

    return (not timedOut)


def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print(f"errorCode lookup failed.  KeyError: {e}")
        sys.exit()
    return key  


# Controller has:
# Motor x2
# currentAxis
# port
# something to check whether a port is in use (ttyUSB0.lock)
class Controller:

    def __init__():


        return

    def getPort():
        currentPort="NO_PORT"
        with open(PORTFILE, 'r') as file:
            currentPort = file.readline().rstrip()
        return currentPort
    
    def _findPorts():
        # 
        ttyUSB_ports = os.listdir('/dev/ttyUSB*')

        # Return the list of found ttyUSB ports
        return ttyUSB_ports

    def getMotors():

        return
    
    def getUART01_Address( port ):

        if port is None:
            ttyUSB_ports = self._findPorts()
            print("Need to specify which port to access variables from.  Possible ports are ", ttyUSB_ports)
            sys.exit()
        
        getBool, UART = reportXCD2noAxisPort(port, ['UART0_ADDRESS', 'UART1_ADDRESS'])

        if getBool==False:
            print("CRITICAL FAILURE. Communication error. ttyUSB found but not corresponding to valide motor axis.")
            sys.exit()

        UART0 = int(UART[0])
        UART1 = int(UART[1])`
    
        return UART0, UART1
    
    def updatePorts():

        # create lookup table of axis variables to compare UART addresses to
        IDlookup = {v:k for k, v in AXID.items()}

        # find open ports
        ttyUSB_ports = _findPorts()

        with open(filename, "w") as file:

            # then for each port find UART addresses and reverse lookup motor IDs
            for port in ttyUSB_ports:

                # now get
                UART0, UART1 = getUART01_Address(port)

                motorID1str = IDlookup[UART0]
                motorID2str = IDlookup[UART1]
            
                # Logs the change to the log for a change
                file.write('%s %s %s\n' % (motorID1str, port, '0'))
                file.write('%s %s %s\n' % (motorID2str, port, '1'))

        return



# Motor class
# port
# name
# typeOfMotor
# axis
# access to kfdb to read positions or other properties we store
# writing to kfdb must be done serially, so maybe it prints write requests
# in full lines to the screen for humans to copy/paste?
class Motor:
 
    # constructor
    def __init__(self, name):
        # look up if name exists in database file
        # if so assigns name and finds other 

        self.name = name
# function:
#    constructor(name)
#       look up the correct port and axis
#       look for a lockfile on that axis
#       set a lockfile, or return None
#    return the motor 


        self.type = self.getType()
        self.axis = self.getAxis()
        self.port = self.getPort()

        return
    

    # accessors
    def isName():

        return True

    def getType(axisName):
        #return a command lookup table matching the axis.
        #also let us know if the axis is a dogleg, so we know how to behave.
        isDogleg=False
        COMM={}
        if bool(re.match(r'^.+_DL\d_A\d$',axisName)):
            COMM=ALL_COMM['Dogleg']
            isDogleg=True
        elif bool(re.match(r'^.+_TH_S$',axisName)):
            COMM=ALL_COMM['ThetaS']
        elif bool(re.match(r'^.+_TH_L$',axisName)):
            COMM=ALL_COMM['ThetaL']
        elif bool(re.match(r'^.+_PHI$',axisName)):
            COMM=ALL_COMM['Phi']        
        elif bool(re.match(r'^.+_AT$',axisName)):
            COMM=ALL_COMM['Attenuator']
        else:
            print("no match of '%s' to axis types.  Critical failure!"%(axisName))
            sys.exit()
        return isDogleg, COMM

    def getAxis():
        stat,ret =reportXCD2noAxis(['XAXIS'])
        if not stat:
            print("Could not getAxis()")
            sys.exit()
        return int(ret[0])
    
    def getPort():


        return 
    
    def getVar(variable):

############################################################
# REPORTXCD2 SCRIPTS - need to be combined into one getVar()
############################################################

# def reportXCD2( argv ):
#     if argv:
#         if len(argv) > 10:
#             print("Too many variables trying to be assigned.  Max 10 variables can be assigned at once.")
#             return False, 0

#         var_names = argv
#         if debug:
#             print(var_names)
        
#         #getAxis = reportXCD2noAxis(['XAXIS'])[0]

#         ax_int = getAxis()
#         #int(getAxis)
#         #print("reportXCD2 axis=",ax_int)
#         ax_byte = ax_int.to_bytes(1,byteorder='little',signed=True)
#         ax_comm = [int(ax_byte[0])]
        
#         command = [228, 165, 0, 213, 0, 0, 6, 132]
#         count = 0
#         for i in range(0, len(var_names)):
#             var = var_names[i]


#             if var in varDict.keys():
#                 var_num = varDict[var]
#                 u2 = var_num.to_bytes(2,byteorder='little',signed=False)
#                 var_command = [int(u2[0]), int(u2[1])]
#                 command += var_command
#                 count += 2
#             else:
#                 print("Variable name - ", var , " -  not recognized. Variable list given as:")
#                 print(varDict.keys())
#                 return False, 0
            
#             command += ax_comm
#             count += 1

#     else:
#         print("No arguments given. reportXCD2 parameters are: \n \
#                1) Variable- Mandatory, variable to report value of. For full list of variables, refer to variableDictionary. \n \
#                2-10) Variable - Optional, other variables to report. \
#                ")
#         return False, 0

#     # reassign packet length and block length bytes
#     command[4] = int(count+6)
#     command[5] = int(count+3)
#     # add stop byte
#     command += [218]
#     if debug:
#         print(command)

#     # the next portion of code is what establishes communication with the controller
#     # and sends the bytestring command by serial comm
#     # and returns a pair of [succeeded,readbackline]
#     success,ret=sendline(getCurrentPort(),command)
#     if success and debug:
#         print(ret)
#     return success, ret



# def reportXCD2noAxis( argv ):
#     return reportXCD2noAxisPort(getCurrentPort(),argv)

# def reportXCD2noAxisPort(target_port, argv ):
#     if argv:
#         if len(argv) > 10:
#             print("Too many variables trying to be assigned.  Max 10 variables can be assigned at once.")
#             return False, 0

#         var_names = argv
#         if debug:
#             print(var_names)

#         command = [228, 165, 0, 213, 0, 0, 6, 4]
#         count = 0
#         for i in range(0, len(var_names)):
#             var = var_names[i]

#             if var in varDict.keys():
#                 var_num = varDict[var]
#                 u2 = var_num.to_bytes(2,byteorder='little',signed=False)
#                 var_command = [int(u2[0]), int(u2[1])]
#                 command += var_command
#                 count += 2
#             else:
#                 print("Variable name - " , var , " -  not recognized. Variable list given as:")
#                 print(varDict.keys())
#                 return False, 0

#     else:
#         print("No arguments given. reportXCD2 parameters are: \n \
#                1) Variable- Mandatory, variable to report value of. For full list of variables, refer to variableDictionary. \n \
#                2-10) Variable - Optional, other variables to report. \
#                ")
#         return False, 0

#     # reassign packet length and block length bytes
#     command[4] = int(count+6)
#     command[5] = int(count+3)
#     # add stop byte
#     command += [218]
#     if debug:
#         print(command) 

#     # the next portion of code is what establishes communication with the controller
#     # and sends the bytestring command by serial comm
#     success,ret=sendline(target_port,command)
#     if success and debug:
#         print(ret)
#     return success, ret
        return
    

    # mutators
    def setVar(variable, value):
        if value:
            if len() > 14:
                print("Too many variables trying to be assigned.  Max 7 variables can be assigned at once.")
                return

            var_names = argv[::2]
            real_vals = argv[1::2]
            if debug:
                print(var_names, real_vals)
            # if len(var_names) != len(real_vals):
            #    print("Formatting error: likely missing/extra variable or value to be assigned. Please check input.")
            #    return

            #getAxis = reportXCD2noAxis(['XAXIS'])[0]

            ax_int = self.getAxis()#int(getAxis)
            #print("writeXCD2 axis=",ax_int)

            ax_byte = ax_int.to_bytes(1,byteorder='little',signed=False)
            ax_comm = [int(ax_byte[0])]


            command = [228, 165, 0, 213, 0, 0, 6, 134]
            count = 0
            for i in range(0, len(var_names)):
                var = var_names[i]
                val = real_vals[i]

                if var in varDict.keys():
                    var_num = varDict[var]
                    u2 = var_num.to_bytes(2,byteorder='little',signed=False)
                    var_command = [int(u2[0]), int(u2[1])]
                    command += var_command
                    count += 2
                else:
                    print("Variable name - " + var + " -  not recognized. Variable list given as:")
                    print(varDict.keys())
                    return

                try:
                    float(val)
                except ValueError:
                    print("Value to assign - " + val + " - must be a real number.")
                    return
                else:
                    number, = struct.unpack('!I', struct.pack('!f', float(val)))
                    r4 = number.to_bytes(4,byteorder='little',signed=False)
                    val_command = [int(r4[0]), int(r4[1]), int(r4[2]), int(r4[3])]
                    command += val_command
                    count += 4

                command += ax_comm
                count += 1
                

                

        else:
            print("No arguments given. writeXCD2 parameters are: \n \
                1) Variable- Mandatory, determines the variable to change the value of. Refer to variableDictionary for a full list of variables. \n \
                2) Value - Mandatory, determines value to change variable to. Real value.  \n ")
            return

        # reassign packet length and block length bytes
        command[4] = int(count+6)
        command[5] = int(count+3)
        # add stop byte
        command += [218]
        if debug:
            print(command)
        # the next portion of code is what establishes communication with the controller
        # and sends the bytestring command by serial comm
        
        success,ret=sendline(getCurrentPort(),command)
        if success and debug:
            print("quickAssign successful:",success,", return value:",ret)
        elif not success and debug:
            print("quickAssign failed:",success,", return value:",ret)

        return success, ret
    
    def home():
        #    go to all the .s19-findable positions: (hard stops, home tick)
        #    check those against the db
        #    if all is well, return true.
        #    if all is not well, update db, print caution to screen with new data.
        return
    
    def gotoStr( str ):
        #    looks up the string in the Db, goes there, returns true if it made it
        return True

    def gotoFloat( val ):
        #    goes to that point, returns true if it made it.
        return True
    
    def __gotoDogleg():
        return
    
    def __gotoPhi():
        return
    
    def __gotoThetaS():
        return
    
    def __gotoThetaL():
        return






    # destructor
    def __del__(self):
        #    removes the lock file
        #    destroys instance of motor
        return

