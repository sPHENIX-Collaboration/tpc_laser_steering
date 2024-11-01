#!/bin/bash

./aimAt.py 9N 15 113
for ((i=114;i<204;i+=1));
do
    ./goto.py 9N_PH "0.${i}";
done

./aimAt.py 9N 25 203
for ((i=204;i>113;i-=1));
do
    ./goto.py 9N_PH "0.${i}";
done