#!/bin/sh
while true; do
    python3 setup.py
    if [[ "$?" == "0"]]; then
        break
    fi
    echo Database is not ready, retying in 5 secs...
    sleep 5
done
flask run