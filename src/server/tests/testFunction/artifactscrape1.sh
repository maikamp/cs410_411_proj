echo Test artifactscrape: curl -s -X POST -d @testartifactscrape1.json crystal.cpi.cs.odu.edu:5000/artifactscrape -o ./curlresponse/addartifactscraperesponse1.txt
curl -s -X POST -d @testartifactscrape1.json crystal.cpi.cs.odu.edu:5000/artifactscrape -o ./curlresponse/addartifactscraperesponse1.txt
cat ./curlresponse/addartifactscraperesponse1.txt | jq '.'