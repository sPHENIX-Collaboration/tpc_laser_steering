#! /usr/bin/python3

from goto import goto
from changeAxisDogleg import changeAxis
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


def wiggleAxis(axis, step=0.01):
    
    return

if __name__ == "__main__":
    if len(sys.argv) == 2:
        axis=sys.argv[1]
        wiggleAxis(axis)
    else:
        print("wiggleAxis.py failed.  Incorrect number of arguments")
        sys.exit()