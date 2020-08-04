echo Test artifactscrape: curl -s -X POST -d @testartifactscrape2.json crystal.cpi.cs.odu.edu:5000/artifactscrape -o ./curlresponse/addartifactscraperesponse2.txt
curl -s -X POST -d @testartifactscrape2.json crystal.cpi.cs.odu.edu:5000/artifactscrape -o ./curlresponse/addartifactscraperesponse2.txt
cat ./curlresponse/addartifactscraperesponse2.txt | jq '.'