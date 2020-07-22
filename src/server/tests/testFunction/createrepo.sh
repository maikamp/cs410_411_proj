#!/bin/sh
echo Test create repository: curl -X POST -d @testcreaterepo1.json crystal.cpi.cs.odu.edu:5000/createrepo -o ./curlresponse/createreporesponse1.txt
curl -X POST -d @testcreaterepo1.json crystal.cpi.cs.odu.edu:5000/createrepo -o ./curlresponse/createreporesponse1.txt
echo Test create repository: curl -X POST -d @testcreaterepo2.json crystal.cpi.cs.odu.edu:5000/createrepo -o ./curlresponse/createreporesponse2.txt
curl -X POST -d @testcreaterepo2.json crystal.cpi.cs.odu.edu:5000/createrepo -o ./curlresponse/createreporesponse2.txt
