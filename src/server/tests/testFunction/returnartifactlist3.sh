#!/bin/sh
echo Test artifact list2: curl -X POST -d @testreturnartifactlist3.json crystal.cpi.cs.odu.edu:5000/returnlistartifacts -o ./curlresponse/returnartifactlistresponse3.txt
curl -s -X POST -d @testreturnartifactlist3.json crystal.cpi.cs.odu.edu:5000/returnlistartifacts -o ./curlresponse/returnartifactlistresponse3.txt
cat ./curlresponse/returnartifactlistresponse3.txt | jq '.'
