#!/bin/sh
echo Test repo info owned by defaulttest: curl -s -X POST -d @testrepoInfo1.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse1.txt
curl -s -X POST -d @testrepoInfo1.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse1.txt
cat ./curlresponse/repoinforesponse1.txt | jq '.'