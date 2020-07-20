#!/bin/sh
echo Test artifact info: curl -X POST -d @artifactInfo.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo
curl -X POST -d @artifactInfo.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo
echo Test artifact info 2: curl -X POST -d @artifactInfo2.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo
curl -X POST -d @artifactInfo2.json crystal.cpi.cs.odu.edu:5000/returnartifactinfo
