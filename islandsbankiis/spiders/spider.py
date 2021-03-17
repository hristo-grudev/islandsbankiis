import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import IslandsbankiisItem
from itemloaders.processors import TakeFirst

base = 'https://www.islandsbanki.is/publicapi/is/newslist/?arrayOfFilters=news&quantity=100&page={}'

class IslandsbankiisSpider(scrapy.Spider):
	name = 'islandsbankiis'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		for post in data['data']['results']:
			date = post['first_publication_date']
			url = post['href']
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		total_pages = data['data']['total_pages']
		if self.page < total_pages:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date):
		data = json.loads(response.text)
		title = data['results'][0]['data']['shareTitle'][0]['text']
		try:
			description = data['results'][0]['data']['shareDescription'][0]['text']
		except:
			description = ''

		item = ItemLoader(item=IslandsbankiisItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
