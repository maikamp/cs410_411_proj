#!/bin/sh
echo Test upload 1: curl -s -H "Content-Type:multipart/form-data" -F "meta-data=@testartifactupload1.json" -F "file=@simplemd.md" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse1.txt
curl -s -H "Content-Type:multipart/form-data" -H "Content-Type: application/json" -F "meta-data=@testartifactupload1.json" -H "Content-Type: application/octet-stream" -F "file=@simplemd.md" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse1.txt
cat ./curlresponse/artifactuploadresponse1.txt | jq '.'