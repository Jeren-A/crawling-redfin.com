from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CredfinSpider(CrawlSpider):
    name = 'credfin'
    allowed_domains = ['redfin.com']
    start_urls = ('http://redfin.com/',)

    rules = (Rule(LinkExtractor(deny_domains = ('facebook.com', 'twitter.com', 'pinterest.com', 'instagram.com')), callback = 'parse_page', follow=True),)

    def parse_page(self, response):
        yield {'URL':response.url}
