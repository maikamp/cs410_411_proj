#!/bin/sh
echo Test artifact info: curl -s -X POST -d @testsimplecompare.json crystal.cpi.cs.odu.edu:5000/simplecompare -o ./curlresponse/simplecompareresponse.txt
curl -s -X POST -d @testsimplecompare.json crystal.cpi.cs.odu.edu:5000/simplecompare -o ./curlresponse/simplecompareresponse.txt
cat ./curlresponse/simplecompareresponse.txt
