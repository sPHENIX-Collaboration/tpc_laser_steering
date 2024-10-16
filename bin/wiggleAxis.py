#! /usr/bin/python3

from quickReport import readback
from goto import goto
from changeAxisDogleg import changeAxis
from variableDictionaryXCD2 import varInterfaceAddresses as ADDR
import sys


def _reverseLookup(dict,val):
    #set up the reverse dictionary
    reverse_mapping={v: k for k, v in dict.items()}
    try:
        key=reverse_mapping[val]
    except KeyError as e:
        print(f"_reverseLookup failed.  KeyError: {e}")
        sys.exit()
    return key  


def wiggleAxis(axis, step=0.01, loop=True):
    position = readback(ADDR['FPOS'])
    dest1 = position - step
    dest2 = position + step
    while loop:
        goto(axis, dest1)
        goto(axis, dest2)
    return


if __name__ == "__main__":
    if len(sys.argv) == 2:
        axis=sys.argv[1]
        wiggleAxis(axis)
    elif len(sys.argv) == 3:
        axis=sys.argv[1]
        step=sys.argv[2]
        wiggleAxis(axis, step)
    else:
        print("wiggleAxis.py failed.  Incorrect number of arguments.")
        sys.exit()