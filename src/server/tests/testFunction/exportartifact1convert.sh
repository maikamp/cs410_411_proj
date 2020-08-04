#!/bin/sh
echo Test artifact_export 1: curl -s -X POST -d @testexportArtifact1convert.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse1convert.html
curl -s -X POST -d @testexportArtifact1convert.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse1convert.html 
cat ./curlresponse/exportartifactresponse1convert.html
