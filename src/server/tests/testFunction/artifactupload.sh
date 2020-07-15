#!/bin/sh
echo Test artifact upload 5: curl -F 'filex=@testartifactupload1.json' -F 'filey=@adduser.sh' crystal.cpi.cs.odu.edu:5000/artifactupload
curl -F 'filex=@testartifactupload1.json' -F 'filey=@adduser.sh' crystal.cpi.cs.odu.edu:5000/artifactupload
echo Test artifact upload default: curl -F 'filex=@testartifactupload2.json' -F 'filey=@register.sh' crystal.cpi.cs.odu.edu:5000/artifactupload
curl -F 'filex=@testartifactupload2.json' -F 'filey=@register.sh' crystal.cpi.cs.odu.edu:5000/artifactupload