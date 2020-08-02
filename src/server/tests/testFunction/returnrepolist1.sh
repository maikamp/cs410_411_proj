#!/bin/sh
echo Test repolist1: curl -X POST -d @testreturnrepolist1.json crystal.cpi.cs.odu.edu:5000/returnlistrepos -o ./curlresponse/returnrepolistresponse1.txt
curl -s -X POST -d @testreturnrepolist1.json crystal.cpi.cs.odu.edu:5000/returnlistrepos -o ./curlresponse/returnrepolistresponse1.txt
cat ./curlresponse/returnrepolistresponse1.txt | jq '.'
