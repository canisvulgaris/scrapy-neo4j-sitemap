from scrapy.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.item import Item, Field
from py2neo import Graph
from py2neo import Node
from py2neo import Relationship
import re

graph = Graph("http://neo4j:pass@localhost:7474/db/data/")

class MyItem(Item):
    url= Field()
    title= Field()
    rootPath= Field()
    domain= Field()
    parent= Field()

class MySpider(CrawlSpider):
    name = 'ansible.com'
    allowed_domains = ['ansible.com']
    start_urls = ['https://www.ansible.com/']

    custom_settings = {
        'DEPTH_LIMIT': '2',
        'COOKIES_ENABLED': False
    }

    DOWNLOADER_MIDDLEWARES = {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }

    # set follow to True to parse through all links recursively
    rules = (Rule(LinkExtractor(), callback='parse_url', follow=True), )

    def parse_url(self, response):
        item = MyItem()
        titleName = re.search('<title>(.*)<\/title>', response.xpath('//title').extract_first()).group(1)
        rootPath = re.search('\.com(\/[A-z0-9-]*)', response.url).group(1)
        domain = re.search('^(http|https):\/\/([A-z0-9-.]*\.com)', response.url).group(2)
        parentUrl = ''
        try:
            parentUrl = response.request.headers['Referer'].decode("utf-8")
        except:
            print("cannot find referer");

        item['url'] = response.url
        item['parent'] = parentUrl
        item['domain'] = domain
        item['rootPath'] = rootPath
        item['title'] = titleName

        print("CREATING NEW NODE")
        #print("CREATE (`"+ response.url +"`:page {url:'"+ response.url +"', parent:'"+ parentUrl +"', domain:'"+ domain +"', rootPath:'"+ rootPath +"'})")
        graph.run("CREATE (`"+ response.url +"`:page {url:'"+ response.url +"', parent:'"+ parentUrl +"', domain:'"+ domain +"', rootPath:'"+ rootPath +"'})")

        if parentUrl != '':
            parentNode = ''
            parentNode = graph.run("MATCH (page {url: '"+ parentUrl +"'}) RETURN page.url");
            if parentNode != '':
                print("CREATING RELATIONSHIP TO PARENT")
                #print("MATCH (a:page),(b:page) WHERE a.url = '"+ response.url +"' AND b.url = '"+parentUrl+"' CREATE (a)-[r:link { name: a.name + '<->' + b.name }]->(b) RETURN r")
                graph.run("MATCH (a:page),(b:page) WHERE a.url = '"+ response.url +"' AND b.url = '"+parentUrl+"' CREATE (a)-[r:link { name: a.name + '<->' + b.name }]->(b) RETURN r")

        return item