#!/bin/bash

# create a virtual env if not existing
if [ ! -d venv ]
then
    virtualenv --python=python3 venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# reset the results folder

rm -rf ./results
mkdir ./results

# launch the Zanata script

python3 ./read_zanata_stats.py