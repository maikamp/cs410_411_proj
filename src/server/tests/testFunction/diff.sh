#!/bin/sh
echo Test diff: curl -X POST -d @testdiff.json crystal.cpi.cs.odu.edu:5000/diff -o ./curlresponse/diffresponse.txt
curl -X POST -d @testdiff.json crystal.cpi.cs.odu.edu:5000/diff -o ./curlresponse/diffresponse.txt