#!/bin/sh
echo Test artifact export: curl -X POST -d @exportArtifact.json crystal.cpi.cs.odu.edu:5000/exportartifact
curl -X POST -d @exportArtifact.json crystal.cpi.cs.odu.edu:5000/exportartifact
curl -X POST -d @exportArtifact2.json crystal.cpi.cs.odu.edu:5000/exportartifact
