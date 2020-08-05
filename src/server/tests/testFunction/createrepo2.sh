#!/bin/sh
echo Test create repository named testrepo2 owned by registertest public: curl -s -X POST -d @testcreaterepo2.json crystal.cpi.cs.odu.edu:5000/createrepo -o ./curlresponse/createreporesponse2.txt
curl -s -X POST -d @testcreaterepo2.json crystal.cpi.cs.odu.edu:5000/createrepo -o ./curlresponse/createreporesponse2.txt
cat ./curlresponse/createreporesponse2.txt | jq '.'