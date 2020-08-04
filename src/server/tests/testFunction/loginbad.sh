#!/bin/sh
echo Test bad login: curl -s -X POST -d @testloginbad.json crystal.cpi.cs.odu.edu:5000/login -o ./curlresponse/loginresponsebad.txt
curl -s -X POST -d @testloginbad.json crystal.cpi.cs.odu.edu:5000/login -o ./curlresponse/loginresponsebad.txt
cat ./curlresponse/loginresponsebad.txt | jq '.'