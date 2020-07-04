#!/bin/sh
for i in 1 2
do
    python3 setup.py
    echo Database is not ready, retrying in 30 secs...
    sleep 30
done
flask run