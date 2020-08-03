#!/bin/sh
echo Test artifact list2: curl -X POST -d @testreturnartifactlist2.json crystal.cpi.cs.odu.edu:5000/returnlistartifacts -o ./curlresponse/returnartifactlistresponse2.txt
curl -s -X POST -d @testreturnartifactlist2.json crystal.cpi.cs.odu.edu:5000/returnlistartifacts -o ./curlresponse/returnartifactlistresponse2.txt
cat ./curlresponse/returnartifactlistresponse2.txt | jq '.'
