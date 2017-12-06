import scrapy
import logging
from datetime import datetime as dt
from scrapy.utils.log import configure_logging

class Sbspider(scrapy.Spider):
    """
    Spider for extracting data from http://www.strandbooks.com/events/
    Usage: scrapy crawl sbspider -o file_name.json
    """
    name = "sbspider"
    
    # Logging spider output
    time_for_log = dt.now().strftime('-%d%m%y-%H%M%S')
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename=name+time_for_log+'.log',
        format='%(levelname)s: %(message)s',
        level=logging.INFO,
    #    stream=sys.stdout,
    )
    
    def start_requests(self):
        urls = ["http://www.strandbooks.com/events/"]
        yield scrapy.Request(url=urls[0], callback=self.parse_page_with_events)
    
    def parse_page_with_events(self, response):
        
        # Extarct list of events urls on page
        events_urls = response.xpath('//*[@id="calendar"]/div[@class="calendar__container"]/div[@class="events__list-group"]/div[@class="events__list-item"]/h3/a/@href').extract()
        
        # Additional check that events urls present on page
        if len(events_urls) != 0:
            
            # requests each event page for parsing
            for url in events_urls:
                yield scrapy.Request(url=url, callback=self.parse_event_page)
        else:
            logging.info("\nevents_urls list empty! Seems events ended.\n")
            return "\nevents_urls list empty! Seems events ended.\n"
    
        next_page = response.xpath('//*[@class="calendar__footer"]/div[@class="calendar__navigation"]/a[2]/@href').extract_first()
        
        if next_page is not None:
            next_page = response.urljoin(next_page)
            logging.info("\n>>>>>>>>>>>>>>>>>>> NEXT PAGE >>>>>>>>>>>>>>>>>>>>>\n")
            yield response.follow(next_page, callback=self.parse_page_with_events)
        else:
            yield "\nSeems next_page is None\n"
    
    def parse_event_page(self, response):
        event_title = response.xpath('//*/div[@class="event"]/h3/text()').extract_first()
        description = response.xpath('//*/div[@class="event"]/div[@class="event__info"]/div[@class="event__description"]').extract_first()
        date_from_raw = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-start"]/abbr/@title').extract_first()
        date_from = dt.strptime(date_from_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        
        # Checking if DateTo present on page. If not, will be used date_from value
        # date_to located in abbr tag with class='value date'
        is_it_date_to = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr/@class').extract_first()

        if is_it_date_to == 'value date':
            date_to_raw = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr/@title').extract_first()
            date_to = dt.strptime(date_to_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
        else:
            date_to = date_from
            
        start_time_raw = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-start"]/abbr[@class="value time"]/text()').extract_first().strip()
        start_time = start_time_raw[:-2] + ' ' + start_time_raw[-2:].lower()
        
        end_time_raw = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr[@class="value time"]/text()').extract_first().strip()
        end_time = end_time_raw[:-2] + ' ' + end_time_raw[-2:].lower()
        
        event_web_site = response.url
        event_img_raw = response.xpath('//*/div[@class="event__image"]/img/@src').extract_first()
        event_img = response.urljoin(event_img_raw)
        
        return dict({
            "title": event_title,
            "organization": "",
            "description": description,
            "dateFrom": date_from,
            "dateTo": date_to,
            "startTime": start_time,
            "endTime": end_time,
            "eventWebsite": event_web_site,
            "In_group_id": "",
            "ticketUrl": event_web_site,
            "eventImage": event_img,
            "street": "",
            "city": "",
            "state": "",
            "zip": "",
        })