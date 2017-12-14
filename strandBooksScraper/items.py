# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.exceptions import DropItem
from scrapy.loader.processors import Compose, TakeFirst

def name_filter(name):
	ignore_words = re.search('Book Discussion', name)
	if ignore_words:
		raise DropItem("Ignore event")
	else:
		return name.encode().decode()

def time_converter(raw_time):
	raw_time.strip()
	hour = int(re.findall('(\d{1,2}):\d{2}', raw_time)[0])
	minute = re.findall('\d{1,2}:(\d{2})', raw_time)[0]
	if hour < 13:
		return '{}:{} {}'.format(str(hour), minute, 'am')
	else:
		return '{}:{} {}'.format(str(hour-12), minute, 'pm')
		
def date_converter(raw_date):
	yyyy = re.findall('(\d{4})-\d{2}-\d{2}', raw_date)[0]
	mm = re.findall('\d{4}-(\d{2})-\d{2}', raw_date)[0]
	dd = re.findall('\d{4}-\d{2}-(\d{2})', raw_date)[0]
	return '{}/{}/{}'.format(dd, mm, yyyy)

class StrandbooksscraperItem(scrapy.Item):
	
	organization = scrapy.Field(
		output_processor=TakeFirst(),
		)#rich text format - no special chars
	title = scrapy.Field(
		input_processor=Compose(TakeFirst(), name_filter),
		output_processor=TakeFirst(),
		)#rich text format - no special chars
	description = scrapy.Field(
		output_processor=TakeFirst(),
		)
	eventWebsite = scrapy.Field(
		output_processor=TakeFirst(),
		)#full link! Hard-code http://.... if missing!
	street = scrapy.Field(
		output_processor=TakeFirst(),
		)#rich text format - no special chars
	city = scrapy.Field(
		output_processor=TakeFirst(),
		)#rich text format - no special chars
	state = scrapy.Field(
		output_processor=TakeFirst(),
		)#rich text format - no special chars
	zip = scrapy.Field(
		output_processor=TakeFirst(),
		)#numerical fromat required: xxxxx
	dateFrom = scrapy.Field(
		input_processor=Compose(TakeFirst(), date_converter),
		output_processor=TakeFirst(),
		)# Only acceptable format is dd/mm/yyyy !! - ex: 19/12/2017
	startTime = scrapy.Field(
		input_processor=Compose(TakeFirst(), time_converter),
		output_processor=TakeFirst(),
		)# Only acceptable format is hh:mm am/pm !! - ex: 07:45 pm
	In_group_id = scrapy.Field(
		output_processor=Compose(lambda v: v[0]),
		)# should be empty! will code that later
	ticketUrl = scrapy.Field(
		output_processor=TakeFirst(),
		)#full link! Hard-code http://.... if missing!
	eventImage = scrapy.Field(
		output_processor=TakeFirst(),
		)#full link! Hard-code http://.... if missing! Leave empty if event image is missing!
	dateTo = scrapy.Field(
		input_processor=Compose(TakeFirst(), date_converter),
		output_processor=TakeFirst(),
		)#(REQUIRED FORMAT: dd/mm/yyyy)
	endTime = scrapy.Field(
		input_processor=Compose(TakeFirst(), time_converter),
		output_processor=TakeFirst(),
		)#(REQUIRED FORMAT: hh:mm am/pm)