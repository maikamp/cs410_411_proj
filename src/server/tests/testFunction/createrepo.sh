#!/bin/sh
echo Test create repository: curl -X POST -d @testcreaterepo1.json crystal.cpi.cs.odu.edu:5000/createrepo
curl -X POST -d @testcreaterepo1.json crystal.cpi.cs.odu.edu:5000/createrepo
echo Test create repository: curl -X POST -d @testcreaterepo2.json crystal.cpi.cs.odu.edu:5000/createrepo
curl -X POST -d @testcreaterepo2.json crystal.cpi.cs.odu.edu:5000/createrepo
