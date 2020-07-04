#!/bin/sh
for i in 1 2 3
do
    python3 setup.py
    echo Database is not ready, retrying in 5 secs...
    sleep 5
done
flask run