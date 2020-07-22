#!/bin/sh
echo Test artifact info: curl -X POST -d @testsimplecompare.json crystal.cpi.cs.odu.edu:5000/simplecompare
curl -X POST -d @testsimplecompare.json crystal.cpi.cs.odu.edu:5000/simplecompare

