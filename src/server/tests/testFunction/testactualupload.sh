#!/bin/sh
echo curl -F files=@testartifactupload1.json \-F files=@../../simplemd.md crystal.cpi.cs.odu.edu:5000/artifactupload 
#curl -X POST -d @testartifactupload1.json crystal.cpi.cs.odu.edu:5000/artifactupload
curl -F files=@testartifactupload1.json \-F files=@../../simplemd.md crystal.cpi.cs.odu.edu:5000/artifactupload 