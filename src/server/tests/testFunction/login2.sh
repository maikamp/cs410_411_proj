#!/bin/sh
echo Test login: curl -s -X POST -d @testlogin2.json crystal.cpi.cs.odu.edu:5000/login -o ./curlresponse/loginresponse2.txt
curl -s -X POST -d @testlogin2.json crystal.cpi.cs.odu.edu:5000/login -o ./curlresponse/loginresponse2.txt
cat ./curlresponse/loginresponse2.txt | jq '.'
