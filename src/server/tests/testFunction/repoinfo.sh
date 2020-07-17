#!/bin/sh
echo Test repo info: curl -X POST -d @repoInfo.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo
curl -X POST -d @repoInfo.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo
