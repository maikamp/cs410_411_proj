#!/bin/sh
echo Test upload 1 changed: curl -v -H "Content-Type:multipart/form-data" -F "meta-data=@testartifactupload1changed.json" -F "file=@simplemd.md" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse1changed.txt
curl -v -H "Content-Type:multipart/form-data" -H "Content-Type: application/json" -F "meta-data=@testartifactupload1changed.json" -H "Content-Type: application/octet-stream" -F "file=@simplemd.md" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse1changed.txt
