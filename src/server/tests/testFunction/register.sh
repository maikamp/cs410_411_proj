#!/bin/sh
echo Test register: curl -X POST -d @testregister.json crystal.cpi.cs.odu.edu:5000/register
curl -X POST -d @testregister.json crystal.cpi.cs.odu.edu:5000/register
