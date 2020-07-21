#!/bin/sh
echo Test login: curl -X POST -d @testlogin.json crystal.cpi.cs.odu.edu:5000/login
curl -X POST -d @testlogin.json crystal.cpi.cs.odu.edu:5000/login
