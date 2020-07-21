#!/bin/sh
echo Test adduser 5: curl -X POST -d @testadduser1.json crystal.cpi.cs.odu.edu:5000/adduser
curl -X POST -d @testadduser1.json crystal.cpi.cs.odu.edu:5000/adduser
echo Test adduser default: curl -X POST -d @testadduser2.json crystal.cpi.cs.odu.edu:5000/adduser
curl -X POST -d @testadduser2.json crystal.cpi.cs.odu.edu:5000/adduser

