#!/bin/sh
echo curl -X POST -d @testartifactupload1.json crystal.cpi.cs.odu.edu:5000/artifactupload
curl -X POST -d @testartifactupload1.json crystal.cpi.cs.odu.edu:5000/artifactupload