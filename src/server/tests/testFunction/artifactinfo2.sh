#!/bin/sh
echo Test artifact info 2: curl -s -X POST -d @testartifactInfo2.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo -o ./curlresponse/artifactinforesponse2.txt
curl -s -X POST -d @testartifactInfo2.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo -o ./curlresponse/artifactinforesponse2.txt
cat ./curlresponse/artifactinforesponse2.txt | jq '.'