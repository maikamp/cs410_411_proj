#!/bin/sh
echo Test login: curl -s -X POST -d @testlogin1.json crystal.cpi.cs.odu.edu:5000/login -o ./curlresponse/loginresponse1.txt
curl -s -X POST -d @testlogin1.json crystal.cpi.cs.odu.edu:5000/login -o ./curlresponse/loginresponse1.txt
cat ./curlresponse/loginresponse1.txt | jq '.'
