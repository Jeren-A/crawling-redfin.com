import scrapy


class RedfinSpider(scrapy.Spider):

    name = 'redfin'
    allowed_domains = ['https://www.redfin.com/']
    start_urls = ['http://redfin.com/']

    def parse(self, response):


        city = response.xpath('//*[@class="city"]/a/href()').extract()
        state = response.xpath('//*[@class = "state"]/a/href()').extract()

        yield {
            'cities': city, 'states': state
        }

