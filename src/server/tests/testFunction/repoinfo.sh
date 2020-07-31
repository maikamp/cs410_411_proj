#!/bin/sh
echo Test repo info: curl -X POST -d @testrepoInfo.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse.txt
curl -X POST -d @testrepoInfo.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse.txt
