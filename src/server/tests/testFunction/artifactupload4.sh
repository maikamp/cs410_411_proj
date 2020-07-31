#!/bin/sh
echo Test upload 4 BAD: curl -v -H "Content-Type:multipart/form-data" -F "meta-data=@testartifactupload4.json" -F "file=@Examplebad.gif" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse4.txt
curl -v -H "Content-Type:multipart/form-data" -F "file=@Examplebad.gif" crystal.cpi.cs.odu.edu:5000/artifactupload -o ./curlresponse/artifactuploadresponse4.txt
