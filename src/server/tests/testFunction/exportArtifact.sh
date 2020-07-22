#!/bin/sh
echo Test artifact_export 1: curl -X POST -d @testexportArtifact1.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse1.txt
curl -X POST -d @testexportArtifact1.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse1.txt
echo Test artifact_export 2: curl -X POST -d @testexportArtifact2.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse2.txt
curl -X POST -d @testexportArtifact2.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse2.txt
