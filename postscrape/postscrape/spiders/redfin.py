import scrapy


class RedfinSpider(scrapy.Spider):
    #handle_httpstatus_list = [301]
    name = 'redfin'
    allowed_domains = ['redfin.com']
    
    start_urls = ['http://www.redfin.com/']
    #handle_httpstatus_list = [301]


    def parse(self, response):
      
       
        #city = response.xpath('//*[@class="city"]/a/@href()').extract()
        #state = response.xpath('//*[@id="content"]').extract()
  
        pass
        # yield {
        #  'states': state
        # }

