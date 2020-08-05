#!/bin/sh
echo Test repo info as guest is public: curl -s -X POST -d @testrepoInfo4.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse4.txt
curl -s -X POST -d @testrepoInfo4.json crystal.cpi.cs.odu.edu:5000/returnrepoinfo -o ./curlresponse/repoinforesponse4.txt
cat ./curlresponse/repoinforesponse4.txt  | jq '.'