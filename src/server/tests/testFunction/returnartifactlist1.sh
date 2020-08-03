#!/bin/sh
echo Test artifact list1: curl -X POST -d @testreturnartifactlist1.json crystal.cpi.cs.odu.edu:5000/returnlistartifacts -o ./curlresponse/returnartifactlistresponse1.txt
curl -s -X POST -d @testreturnartifactlist1.json crystal.cpi.cs.odu.edu:5000/returnlistartifacts -o ./curlresponse/returnartifactlistresponse1.txt
cat ./curlresponse/returnartifactlistresponse1.txt | jq '.'
