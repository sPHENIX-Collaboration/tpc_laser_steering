#!/bin/python3

# a quick function to set the UARTS on ttyUSB0 and ttyUSB1 so that updatePorts sees two doglegs.
from quickAssign import writeXCD2
from quickReport import readback
from xcdSerial import getCurrentPort
from updatePorts import updatePorts
import sys
import time
from variableDictionaryXCD2 import varUniqueID as ID
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
from variableDictionaryXCD2 import varStatusValues as STAT


#tuning settings
sleeptime=0.5 #in seconds
debug=False
PORTFILE="XCD_current_port"


def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print("reverse lookup failed.  KeyError: %s"%(e))
        sys.exit()
    return key

def assignUARTsToPort(port, id0, id1):
    #print("assigning %s:  ax0:%s ax1:%s"%(port,id0,id1))
    port_before=getCurrentPort()
    with open(PORTFILE, 'w') as file:
        file.write(port)
    oldStatus=readback(ADDR['STATUS'])
    writeXCD2(['UART0_ADDRESS', id0])
    writeXCD2(['UART1_ADDRESS', id1])    
    writeXCD2([ADDR['STATUS'], 0])    #clear the 'boot' status for this board now that we have assigned it.
    writeXCD2([ADDR['XAXIS'], 0]) #always default to axis zero when we're assigning
    #writeXCD2([ADDR['ID'], id0) #and write the proper ID to it.  except this will provoke the changeAxis to overwrite possibly valid data in the file.
    print("assigned %s:  ax0:%s ax1:%s. status:%s==>%s"%(port,id0,id1,oldStatus,readback(ADDR['STATUS'])))

    #return to what the active was before we began:
    with open(PORTFILE, 'w') as file:
        file.write(port_before)

def assignPorts_forEgg(laserPosition):
    #check if laser is in the allowed list:
    valid_names={"3S","6S","9S","12S","3N","6N","9N","12N","DEBUG"}
    if not (laserPosition in valid_names):
        print("Cannot assign ports for laser %s.  Laser must be in the list %s"%(laserPosition,valid_names))
        return False

    #now we are guaranteed we have a valid laser argument
    assignUARTsToPort("/dev/ttyUSB0", ID["%s_TH_S"%(laserPosition)], ID["%s_TH_L"%(laserPosition)])
    assignUARTsToPort("/dev/ttyUSB1", ID["%s_PH"%(laserPosition)], ID["%s_AT"%(laserPosition)])
    

if __name__ == "__main__":

    #check args
    #note that sys.argv has arg 1 as the command itself
    #if wrong arguments, exit with explanation
    if len(sys.argv) == 2: #overall default
        print("Trying to assign ttyUSB0 and USB1 to standard laser egg configuration:")
        assignPorts_forEgg(sys.argv[1])
        print("Note:  This has NOT assigned the ID of the current axis (axis 0), so your first changeAxis will write to junk file and read in from the correct.")
        print("Be sure to changeAxis before you begin to steer.")
        updatePorts()
    else:
        print("NOT EXECUTED. Wrong number of arguments.  Correct usage is ./assignPorts_forEgg.py 12S (etc)")
        sys.exit()
     
    print("Done.")
