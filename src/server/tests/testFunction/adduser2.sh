#!/bin/sh
echo Test adduser default: curl -X POST -d @testadduser2.json crystal.cpi.cs.odu.edu:5000/adduser -o ./curlresponse/adduserresponse2.txt
curl -s -X POST -d @testadduser2.json crystal.cpi.cs.odu.edu:5000/adduser -o ./curlresponse/adduserresponse2.txt
cat ./curlresponse/adduserresponse2.txt | jq '.'
