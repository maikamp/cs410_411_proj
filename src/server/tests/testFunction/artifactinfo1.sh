#!/bin/sh
echo Test artifact info local artifact owned by defaulttest in testrepo1: curl -s -X POST -d @testartifactInfo1.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo -o ./curlresponse/artifactinforesponse1.txt
curl -s -X POST -d @testartifactInfo1.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo -o ./curlresponse/artifactinforesponse1.txt
cat ./curlresponse/artifactinforesponse1.txt | jq '.'
