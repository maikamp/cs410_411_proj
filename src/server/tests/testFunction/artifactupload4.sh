#!/bin/sh
echo Test upload 4 BAD: curl -v -H "Content-Type:multipart/form-data" -F "meta-data=@testartifactupload4.json" -F "file=@Examplebad.gif" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse4.txt
curl -v -H "Content-Type:multipart/form-data" -H "Content-Type: application/json" -F "meta-data=@testartifactupload4.json" -H "Content-Type: application/octet-stream" -F "file=@badToaster.gif" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse4.txt
