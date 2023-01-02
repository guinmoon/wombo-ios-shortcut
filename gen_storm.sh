#!/bin/bash
for (( i=1; i <= 40; i++ ))
do
python3 wombo_create.py -p "$1" -s r -b && python3 wombo_create.py -i && python3 wombo_create.py -d && python3 wombo_create.py -c -r
done
