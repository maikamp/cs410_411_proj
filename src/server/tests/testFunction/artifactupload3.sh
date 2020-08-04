#!/bin/sh
echo Test upload 3 duplicate: curl -s -H "Content-Type:multipart/form-data" -F "meta-data=@testartifactupload3.json" -F "file=@Example.docx" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse3.txt
curl -s -H "Content-Type:multipart/form-data" -H "Content-Type: application/json" -F "meta-data=@testartifactupload3.json" -H "Content-Type: application/octet-stream" -F "file=@Example.docx" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse3.txt
cat ./curlresponse/artifactuploadresponse3.txt | jq '.'
