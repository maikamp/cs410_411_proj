#!/bin/sh
echo Waiting 30 seconds for Database container to be ready....
sleep 30
python3 setup.py
flask run