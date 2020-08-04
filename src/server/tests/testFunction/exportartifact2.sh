#!/bin/sh
echo Test artifact_export 2: curl -s -X POST -d @testexportArtifact2.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse2.txt
curl -s -X POST -d @testexportArtifact2.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse2.txt 
cat ./curlresponse/exportartifactresponse2.txt
