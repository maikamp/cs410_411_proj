#!/bin/sh
echo Test diff: curl -s -X POST -d @testdiff.json crystal.cpi.cs.odu.edu:5000/diff -o ./curlresponse/diffresponse.txt
curl -s -X POST -d @testdiff.json crystal.cpi.cs.odu.edu:5000/diff -o ./curlresponse/diffresponse.txt
cat ./curlresponse/diffresponse.txt 