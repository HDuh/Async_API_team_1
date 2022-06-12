curl -XPUT http://localhost:9200/genres -H 'Content-Type: application/json' -d @/indexes/genres.json
curl -XPUT http://localhost:9200/persons -H 'Content-Type: application/json' -d @indexes/persons.json
curl -XPUT http://localhost:9200/movies -H 'Content-Type: application/json' -d @indexes/movies.json