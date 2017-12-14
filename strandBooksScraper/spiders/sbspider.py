# -*- coding: utf-8 -*-
from scrapy import Request, Spider
from scrapy.loader import ItemLoader
from strandBooksScraper.items import StrandbooksscraperItem

class Sbspider(Spider):
    
    allowed_domains = ['strandbooks.com']
    name = "sbspider"
    
    def start_requests(self):
        # url value is first available page with events in www.strandbooks.com
        url = "http://www.strandbooks.com/index.cfm/fuseaction/event.index/nodeID/a35c34a6-bda5-4733-9f7d-fa7187e8c2e3/?start=%7Bts%20%272015-01-01%2000%3A00%3A00%27%7D&view=list"
        yield Request(url=url, callback=self.parse)
    
    def parse(self, response):
        # Extarct list of events urls on page
        events_urls = response.xpath('//*[@id="calendar"]/div[@class="calendar__container"]/div[@class="events__list-group"]/div[@class="events__list-item"]/h3/a/@href').extract()
        
        # Additional check that events urls present on page
        if len(events_urls) != 0:
            # requests each event page for parsing
            for url in events_urls:
                yield Request(url=url, callback=self.parse_attr)
        else:
            return "\nevents_urls list empty! Seems events ended.\n"
    
        next_page = response.xpath('//*[@class="calendar__footer"]/div[@class="calendar__navigation"]/a[2]/@href').extract_first()
        
        if next_page is not None:
            next_page = response.urljoin(next_page)
            #logging.info("\n>>>>>>>>>>>>>>>>>>> NEXT PAGE >>>>>>>>>>>>>>>>>>>>>\n")
            yield response.follow(next_page, callback=self.parse)
        else:
            yield "\nSeems next_page is None\n"
    
    def parse_attr(self, response):
        title = response.xpath('//*/div[@class="event"]/h3/text()').extract_first()
        description = response.xpath('//*/div[@class="event"]/div[@class="event__info"]/div[@class="event__description"]').extract_first()
        dateFrom_raw = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-start"]/abbr/@title').extract_first()
        
        # Checking if DateTo present on page. If not, will be used dateFrom value
        # dateTo located in abbr tag with class='value date'
        is_it_dateTo = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr/@class').extract_first()

        if is_it_dateTo == 'value date':
            dateTo_raw = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr/@title').extract_first()
        else:
            dateTo_raw = dateFrom_raw
        
        #startTime_raw = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-start"]/abbr[@class="value time"]/text()').extract_first().strip()
        #endTime_raw = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr[@class="value time"]/text()').extract_first().strip()
        eventImage_raw = response.xpath('//*/div[@class="event__image"]/img/@src').extract_first()
        eventImage = response.urljoin(eventImage_raw)
    
        item_loader = ItemLoader(item=StrandbooksscraperItem(), response=response)
        item_loader.add_value('title', title)
        item_loader.add_value('organization', 'Strand Book Store')
        item_loader.add_value('description', description)
        item_loader.add_value('dateFrom', dateFrom_raw)
        item_loader.add_value('dateTo', dateTo_raw)
        item_loader.add_xpath('startTime', '//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-start"]/abbr[@class="value time"]/text()')
        item_loader.add_xpath('endTime', '//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr[@class="value time"]/text()')
        item_loader.add_value('eventWebsite', response.url)
        item_loader.add_value('In_group_id', '')
        item_loader.add_value('eventImage', eventImage)
        item_loader.add_value('ticketUrl', response.url)
        item_loader.add_value('street', '828 Broadway (& 12th Street)')
        item_loader.add_value('city', 'New York')
        item_loader.add_value('state', 'New York')
        item_loader.add_value('zip', 10003)
        return item_loader.load_item()