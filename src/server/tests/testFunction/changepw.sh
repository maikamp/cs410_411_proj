#!/bin/sh
echo Test changepw: curl -X POST -d @testchangepw.json crystal.cpi.cs.odu.edu:5000/changepw
curl -X POST -d @testchangepw.json crystal.cpi.cs.odu.edu:5000/changepw
