#!/bin/sh
echo Test changepw: curl -s -X POST -d @testchangepw.json crystal.cpi.cs.odu.edu:5000/changepw -o ./curlresponse/changepwresponse.txt
curl -s -X POST -d @testchangepw.json crystal.cpi.cs.odu.edu:5000/changepw -o ./curlresponse/changepwresponse.txt
cat ./curlresponse/changepwresponse.txt | jq '.'