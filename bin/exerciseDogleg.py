#! /usr/bin/python3

import time
from updatePorts import find_ttyUSB_ports
import quickAssign
import quickReport
import gotoDogleg



# Iterate over all serial controllers we find matching /dev/ttyUSB*
ttyUSB_ports = find_ttyUSB_ports()
ttyUSB_ports = '/dev/ttyUSB0'
for ser in ttyUSB_ports:
    print(">>>>>>>testing controller on $ser ...")
    print("$ser" > XCD_current_port)

    quickReport

# Iterate over all serial controllers we find matching /dev/ttyUSB*
for ser in /dev/ttyUSB0; do
    # Check if the file exists
    if [ -e "$ser" ]; then
	echo ">>>>>>>testing controller on $ser ..."
	echo "$ser" > XCD_current_port
	echo ">>>>>>>AXIS 0:"
    ./quickReport.py V19 XAXIS
	./quickAssign.py XAXIS 0
        ./quickAssign.py FPOS 0
	./quickAssign.py V11 0
    ./quickReport.py V19 XAXIS
	./gotoDogleg.py 2.9
	./gotoDogleg.py -2.9
	./gotoDogleg.py 0
	echo ">>>>>>>AXIS 1:"
       ./quickAssign.py XAXIS 1
        ./quickAssign.py FPOS 0
	./quickAssign.py V11 0
       ./gotoDogleg.py 2.9
       ./gotoDogleg.py -2.9
       ./gotoDogleg.py 0
    else
        echo "port not found by shell.  Huh?"
    fi
done

