#!/bin/sh
echo Test adduser 5: curl -X POST -d @testadduser1.json crystal.cpi.cs.odu.edu:5000/adduser -o ./curlresponse/adduserresponse1.txt
curl -s -X POST -d @testadduser1.json crystal.cpi.cs.odu.edu:5000/adduser -o ./curlresponse/adduserresponse1.txt
cat ./curlresponse/adduserresponse1.txt | jq '.'
