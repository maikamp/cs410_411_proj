#!/bin/sh
echo Test addtagartifact : curl -X POST -d @testAddTagArtifact1.json crystal.cpi.cs.odu.edu:5000/addtag -o ./curlresponse/addtagartifactresponse1.txt
curl -X POST -d @testAddTagArtifact1.json crystal.cpi.cs.odu.edu:5000/addtag -o ./curlresponse/addtagartifactresponse1.txt
echo Test addtagartifact : curl -X POST -d @testAddTagArtifact2.json crystal.cpi.cs.odu.edu:5000/addtag -o ./curlresponse/addtagartifactresponse2.txt
curl -X POST -d @testAddTagArtifact2.json crystal.cpi.cs.odu.edu:5000/addtag -o ./curlresponse/addtagartifactresponse2.txt