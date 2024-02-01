#!/bin/bash

# Iterate over all serial controllers we find matching /dev/ttyUSB*
for ser in /dev/ttyUSB0; do
    # Check if the file exists
    if [ -e "$ser" ]; then
	echo "resetting controller on $ser ..."
	echo "$ser" > XCD_current_port
	echo ">>>>>>>AXIS 0:"

    ./stopXMS.sh   
    ./startXMS.sh
sleep 1
    ./quickAssign.py V19 0
    ./quickAssign.py XAXIS 0
    ./quickAssign.py VEL 20
    ./quickReport.py V19 VEL
    ./quickAssign.py XAXIS 1
    ./quickAssign.py VEL 20
    ./quickReport.py V19 VEL
    ./quickAssign.py XAXIS 0

    else
        echo "port not found by shell.  Huh?"
    fi
done