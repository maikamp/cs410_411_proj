#!/bin/sh
echo Test 2: curl -X POST -d @test2.json crystal.cpi.cs.odu.edu:5000/login
curl -X POST -d @test2.json crystal.cpi.cs.odu.edu:5000/login
