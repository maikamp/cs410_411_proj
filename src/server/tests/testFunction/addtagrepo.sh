#!/bin/sh
echo Test addtagrepo : curl -X POST -d @testAddTagRepo1.json crystal.cpi.cs.odu.edu:5000/addtag -o ./curlresponse/addtagreporesponse1.txt
curl -X POST -d @testAddTagRepo1.json crystal.cpi.cs.odu.edu:5000/addtag -o ./curlresponse/addtagreporesponse1.txt
echo Test addtagrepo : curl -X POST -d @testAddTagRepo2.json crystal.cpi.cs.odu.edu:5000/addtag -o ./curlresponse/addtagreporesponse2.txt
curl -X POST -d @testAddTagRepo2.json crystal.cpi.cs.odu.edu:5000/addtag -o ./curlresponse/addtagreporesponse2.txt