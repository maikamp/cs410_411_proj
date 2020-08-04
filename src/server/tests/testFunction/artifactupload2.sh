#!/bin/sh
echo Test upload 2 docx: curl -s -H "Content-Type:multipart/form-data" -F "meta-data=@testartifactupload2.json" -F "file=@Example.docx" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse2.txt
curl -s -H "Content-Type:multipart/form-data" -H "Content-Type: application/json" -F "meta-data=@testartifactupload2.json" -H "Content-Type: application/octet-stream" -F "file=@Example.docx" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse2.txt
cat ./curlresponse/artifactuploadresponse2.txt | jq '.'