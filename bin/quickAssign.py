#!/usr/bin/python3
import time
from xcdSerial import sendline, getCurrentPort
from variableDictionaryXCD2 import varDict
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT
from quickReport import getAxis, readback, reportXCD2noAxis
import sys
import struct

debug=False
sleeptime=0.01
timeout=5


def sendcommand(com,arg):
    if debug:
        print("command:  Check status:")
    status=readback(ADDR['STATUS'])
    if status!=STAT['READY']:
        print("NOT EXECUTED.  Error: sendcommand: Controller is not in ready state. sendcommand(com=%s) says status is %s (%s) "%(com,status,_reverseLookup(STAT,status)))
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
        print ("sendcommand: priming status check before wait")
    status=readback(ADDR['STATUS'])
    print("sendcommand(com=%s) says status is %s (%s) "%(com,status,_reverseLookup(STAT,status)))
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

def writeXCD2( argv ):
    if argv:
        if len(argv) > 14:
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

        ax_int = getAxis()#int(getAxis)
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


if __name__ == "__main__":
    debug=True
    writeXCD2(sys.argv[1:])
