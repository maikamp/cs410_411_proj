#!/bin/sh
echo Test adduser 5: curl -X POST -d @testartifactupload1.json crystal.cpi.cs.odu.edu:5000/artifactupload
curl -X POST -d @testartifactupload1.json -F 'filey=@adduser.sh' crystal.cpi.cs.odu.edu:5000/artifactupload
echo Test adduser default: curl -X POST -d @testartifactupload2.json crystal.cpi.cs.odu.edu:5000/artifactupload
curl -X POST -d @testartifactupload2.json -F 'filey=@register.sh' crystal.cpi.cs.odu.edu:5000/artifactupload