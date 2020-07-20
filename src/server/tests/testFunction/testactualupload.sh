#!/bin/sh
echo Test upload: curl -v -H "Content-Type:multipart/form-data" -F "meta-data=@testartifactupload1.json" -F "file=@../../acubed_svr/simplemd.md" crystal.cpi.cs.odu.edu:5000/artifactupload
curl -v -H "Content-Type:multipart/form-data" -F "meta-data=@testartifactupload1.json" -F "file=@../../acubed_svr/simplemd.md" crystal.cpi.cs.odu.edu:5000/artifactupload
