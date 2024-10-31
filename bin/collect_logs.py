#! /usr/bin/python3

import os
import sys
import subprocess
import json

dirAxisLogs="/home/pi/XCDCommandCodes/bin/axisLogs/"
dirPC="/mnt/c/Users/smh28/Documents/Github/tpc_laser_steering/bin/axisLogs/"
masterLog="/home/pi/XCDCommandCodes/bin/master.log"

# create header for laser data JSON file
header={}
header["last"]="helloWorld.py"
header["version"]=2
header["precision"]={"XAXIS":0, "COMMAND":0, "ID":0, "HARD_STOP1":6, "HARD_STOP2":6, "TH_L_GAIN":3, "HOME":6, "ARG":6, \
                     "TURNS":0, "STATUS":0, "FPOS":6, "ENR":9, "KP":0, "KV":9, "LI":0, "FRP":0, "FRN":0}

# create benches to store data from individual benches in JSON file
benches={}

# will become master JSON file, including header and benches
dataLasers={}
dataLasers["header"]=header
dataLasers["benches"]=benches

# collect_logs -tail -2 > head -1 to 

def collect_logs():
    #go to dire
    #reutrn all log files
    #for each log file, tail 2 head 1 to get second to last line --> axis value
    #axis[key]=json.loads(the text)

    # loop through 8 laser benches
    for b in ["3N","6N","9N","12N","3S","6S","9S","12S"]:

        # for each bench create empty dictionary of axes
        axes={}

        # list all relevant axis log files for that bench
        command=['ls', dirAxisLogs+b+'*']
        result=subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)

        # for each axis log file, grab second-to-last entry and store as axis entry in that bench's dictionary
        for log in result:
            grabdata=['tail', '-n', '2', dirAxisLogs+log, '|', 'head', '-n', '1']
            result=subprocess.run(grabdata, capture_output=True, text=True)
            axis=log.rstrip(".log")
            axes[axis]=json.loads(result.stdout)
        
        # lastly assign that bench to the benches dictionary
        benches[b]=axes

    print(json.dumps(dataLasers, indent=4))

    return


if __name__ == "__main__":
    collect_logs()