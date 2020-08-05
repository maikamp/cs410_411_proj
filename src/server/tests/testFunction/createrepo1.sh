#!/bin/sh
echo Test create repository named testrepo1 owned by defaulttest permission 3: curl -s -X POST -d @testcreaterepo1.json crystal.cpi.cs.odu.edu:5000/createrepo -o ./curlresponse/createreporesponse1.txt
curl -s -X POST -d @testcreaterepo1.json crystal.cpi.cs.odu.edu:5000/createrepo -o ./curlresponse/createreporesponse1.txt
cat ./curlresponse/createreporesponse1.txt | jq '.'