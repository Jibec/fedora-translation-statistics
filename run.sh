#!/bin/bash

##################################################
### INITIALIZATION
##################################################

# create a virtual env if not existing
if [ ! -d venv ]
then
    virtualenv --python=python3 venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

##################################################
### ZANATA
##################################################
# reset the results folder

rm -rf ./results
mkdir ./results

# launch the Zanata script

./read_zanata_stats.py

# save data in git

git add history/zanata

git commit -m "add zanata $(date +%F)"

##################################################
### APPDATA FILES
##################################################

for i in {20..30}; do
    ./read_appdata_fedora_stats.py --version "$i"
done

git add history/appdata

git commit -m "add appdata $(date +%F)"
