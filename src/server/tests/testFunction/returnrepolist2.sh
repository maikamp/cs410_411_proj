#!/bin/sh
echo Test repolist2: curl -X POST -d @testreturnrepolist2.json crystal.cpi.cs.odu.edu:5000/returnlistrepos -o ./curlresponse/returnrepolistresponse2.txt
curl -s -X POST -d @testreturnrepolist2.json crystal.cpi.cs.odu.edu:5000/returnlistrepos -o ./curlresponse/returnrepolistresponse2.txt
cat ./curlresponse/returnrepolistresponse2.txt | jq '.'
