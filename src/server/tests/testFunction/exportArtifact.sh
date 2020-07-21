#!/bin/sh
echo Test artifact export: curl -X POST -d @testexportArtifact1.json crystal.cpi.cs.odu.edu:5000/exportartifact
curl -X POST -d @testexportArtifact1.json crystal.cpi.cs.odu.edu:5000/exportartifact
curl -X POST -d @testexportArtifact2.json crystal.cpi.cs.odu.edu:5000/exportartifact
