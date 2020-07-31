#!/bin/sh
echo Test artifact info: curl -X POST -d @testartifactInfo1.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo -o ./curlresponse/artifactinforesponse1.txt
curl -X POST -d @testartifactInfo1.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo -o ./curlresponse/artifactinforesponse1.txt
echo Test artifact info 2: curl -X POST -d @testartifactInfo2.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo -o ./curlresponse/artifactinforesponse2.txt
curl -X POST -d @testartifactInfo2.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo -o ./curlresponse/artifactinforesponse2.txt
