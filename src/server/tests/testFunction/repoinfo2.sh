#!/bin/sh
echo Test repo info not owned but public: curl -s -X POST -d @testrepoInfo2.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse2.txt
curl -s -X POST -d @testrepoInfo2.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse2.txt
cat ./curlresponse/repoinforesponse2.txt