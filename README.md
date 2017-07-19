# scrapy-neo4j-sitemap

Crawls a url using Scrapy and builds a graph in Neo4j.

# install
pip install -r requirements.txt

# set up local neo4j
install neo4j 
run local neo4j service
update neo4j credentials

# run
scrapy runspider crawl.py -o out.json