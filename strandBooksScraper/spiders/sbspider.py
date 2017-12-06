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
        
        # requests each event page for parsing
        if len(events_urls) != 0:
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
        date_from = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-start"]/abbr/@title').extract_first()
        
        # Checking if Date To present on page. If not, will be used date_from value
        is_it_date_to = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr/@class').extract_first()

        if is_it_date_to == 'value date':
            date_to = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr/@title').extract_first()
        else:
            date_to = date_from
            
        start_time = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-start"]/abbr[@class="value time"]/text()').extract_first().strip()
        end_time = response.xpath('//*/div[@class="event__info"]/p[@class="event__date"]/span[@class="event__date-end"]/abbr[@class="value time"]/text()').extract_first().strip()
        event_web_site = response.url
        event_img_raw = response.xpath('//*/div[@class="event__image"]/img/@src').extract_first()
        event_img = response.urljoin(event_img_raw)
        
        return dict({
            "EventTitle": event_title, #Mandatory field
            "Organization": "",
            "Description": description,
            "DateFrom": date_from, #Mandatory field
            "DateTo": date_to,
            "StartTime": start_time, #Mandatory field
            "EndTime": end_time,
            "EventWebsite": event_web_site, #Mandatory field
            "RSVP_URL_or_Email": "",
            "Speaker(s)": "",
            "RelatedImage": event_img,
            "Address": "",
            "RoomNumber": "",
            "ContactName": "",
            "ContactEmail": "",
            "ContactPhone": "",
            "EventPrice": "",
            "Keywords": "" ,
            "Hashtag": ""
        })