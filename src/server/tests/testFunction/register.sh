#!/bin/sh
echo Test register: curl -s -X POST -d @testregister.json crystal.cpi.cs.odu.edu:5000/register -o ./curlresponse/registerresponse.txt
curl -s -X POST -d @testregister.json crystal.cpi.cs.odu.edu:5000/register -o ./curlresponse/registerresponse.txt
cat ./curlresponse/registerresponse.txt |jq '.'