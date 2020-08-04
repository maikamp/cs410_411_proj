#!/bin/sh
echo Test artifact_export 1: curl -s -X POST -d @testexportArtifact1.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse1.docx
curl -s -X POST -d @testexportArtifact1.json crystal.cpi.cs.odu.edu:5000/exportartifact -o ./curlresponse/exportartifactresponse1.docx 
echo this is a docx file and will crash the system so it will not be opened.
