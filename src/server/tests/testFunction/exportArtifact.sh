#!/bin/sh
echo Test artifact info: curl -X POST -d @exportArtifact.json crystal.cpi.cs.odu.edu:5000/exportartifact
curl -X POST -d @exportArtifact.json crystal.cpi.cs.odu.edu:5000/exportartifact
