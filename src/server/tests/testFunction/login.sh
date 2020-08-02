#!/bin/sh
echo Test login: curl -X POST -d @testlogin.json crystal.cpi.cs.odu.edu:5000/login -o ./curlresponse/loginresponse.txt
curl -s -X POST -d @testlogin.json crystal.cpi.cs.odu.edu:5000/login -o ./curlresponse/loginresponse.txt
cat ./curlresponse/loginresponse.txt | jq '.'
