#!/bin/sh
echo Test repo info as guest for not public: curl -s -X POST -d @testrepoInfo3.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse3.txt
curl -s -X POST -d @testrepoInfo3.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse3.txt
cat ./curlresponse/repoinforesponse3.txt  | jq '.'