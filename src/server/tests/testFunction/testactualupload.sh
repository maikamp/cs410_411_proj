#!/bin/sh
echo curl -F files=@testartifactupload1 crystal.cpi.cs.odu.edu:5000/artifactupload \-F files=@../../simplemd.md 
#curl -X POST -d @testartifactupload1.json crystal.cpi.cs.odu.edu:5000/artifactupload
curl -F files=@testartifactupload1 crystal.cpi.cs.odu.edu:5000/artifactupload \-F files=@../../simplemd.md 