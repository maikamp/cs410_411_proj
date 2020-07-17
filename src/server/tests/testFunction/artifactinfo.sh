#!/bin/sh
echo Test artifact info: curl -X POST -d @artifactInfo.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo
curl -X POST -d @artifactInfo.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo
