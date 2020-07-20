#!/bin/sh
echo curl -F files=@testartifactupload1.json \ files=@../../simplemd.md crystal.cpi.cs.odu.edu:5000/artifactupload 
#curl -X POST -d @testartifactupload1.json crystal.cpi.cs.odu.edu:5000/artifactupload
curl -v -H "Content-Type:multipart/form-data" meta-data=@testartifactupload1.json -F file=@../../simplemd.md crystal.cpi.cs.odu.edu:5000/artifactupload
#curl -v -H "Content-Type:multipart/form-data" -F "meta-data=@C:\Users\saurabh.sharma\Desktop\test.json;type=application/json" -F "file-data=@C:\Users\saurabh.sharma\Pictures\Saved Pictures\windows_70-wallpaper.jpg" http://localhost:7002/test/upload