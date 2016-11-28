import scrapy
from scrapy import log
from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import Request
from propertywala.items import PropertywalaItem
from scrapy.loader import ItemLoader
import time
import datetime
import re
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

class PropWala(CrawlSpider):
	name = "propertywalaMumbai"
	allowed_domains = ['propertywala.com']
	start_urls = [ "https://www.propertywala.com/properties/type-residential/for-sale/location-mumbai_maharashtra",
		"https://www.propertywala.com/properties/type-residential_apartment_flat/for-rent/location-mumbai_maharashtra"
		]      
	
	item = PropertywalaItem()
	maxPage = 0

	def parse(self, response):
		hxs = Selector(response)
		data = hxs.xpath('//li[@class="posted"]')

		for i in data:
			'''
			Extracting the urls for each property and jump to new page of that property
			'''
			url = 'https://www.propertywala.com/'+i.xpath('text()').extract_first().strip().encode('ascii', 'ignore').decode('ascii').replace('ID: ','').replace('  Posted:','')
			
			yield Request(url,callback=self.parse1,dont_filter=True)

		next = response.xpath('//div[@class="paging"]/a[last()-1]/@href').extract_first()
		nextPage = int(next.split('=')[-1])
		if (not '?' in str(response.url)):
			self.maxPage = int(response.xpath('//div[@class="paging"]/a[last()]/@href').extract_first().split('=')[-1])
		if ((not next==None) and (nextPage <= self.maxPage)):
			next_url = 'https://www.propertywala.com/'+next
			yield Request(next_url,callback=self.parse)

	def parse1(self,response):
		hxs = Selector(response)

		self.item['Selling_price'] = '0'
		self.item['Possession'] = '0'
		self.item['Status'] = 'None'
		self.item['carpet_area'] = '0'
		self.item['management_by_landlord'] = 'None'
		self.item['areacode'] = 'None'
		self.item['mobile_lister'] = 'None'
		self.item['google_place_id'] = 'None'
		self.item['Launch_date'] = '0'
		self.item['age'] = 'None'
		self.item['address'] = 'None'
		self.item['price_on_req'] = 'false'
		self.item['Details'] = 'None'
		self.item['Monthly_Rent'] = '0'
		self.item['sublocality'] = 'None'
		self.item['price_per_sqft'] = '0'
		self.item['listing_by'] = 'None'
		self.item['name_lister'] = 'None'


		self.item['city'] = 'Mumbai'
		self.item['platform'] = 'propertywala'
		self.item['property_type'] = 'Residential'

		self.item['lat'] = response.xpath('//meta[@property="og:latitude"]/@content').extract_first()

		self.item['longt'] = response.xpath('//meta[@property="og:longitude"]/@content').extract_first()

		self.item['data_id'] = response.url.split('/')[-1]

		dat = response.xpath('//li[@class="noPrint"]/time/@datetime').extract_first().replace('Z','')
		print dat
		self.item['listing_date'] = dt.strftime(dt.strptime(dat,'%Y-%m-%d %H:%M:%S'),'%m/%d/%Y %H:%M:%S')

		self.item['updated_date'] = self.item['listing_date']

		conf = response.xpath('//h2[@id="AutoGeneratedTitle"]/text()').extract_first()
		bed = re.findall('[0-9]',conf)
		if bed:
			self.item['config_type'] = bed[0]+'BHK'
		if not bed:
			self.item['config_type'] = 'None'

		loc = response.xpath('//div[@id="PropertyDetails"]/section/header/h4/text()').extract_first().strip().split(',')
		self.item['locality'] = loc[len(loc) - 2]

		build = response.xpath('//div[@id="PropertyDetails"]/section/header/h3/text()').extract_first().strip()
		buildname = re.findall('for sale in (.*)?,',conf)+re.findall('for rent in (.*)?,',conf)
		print buildname
		if buildname:
			self.item['Building_name'] = buildname[0].split(',')[0].strip()
		else:
			self.item['Building_name'] = 'None'
		if (self.item['Building_name'] in self.item['locality']) or (self.item['locality'] in self.item['Building_name']):
			self.item['Building_name'] = re.findall(' in (.*)?,',build)+re.findall(' at (.*)?,',build)
			if self.item['Building_name']:
				self.item['Building_name'] = self.item['Building_name'][0].strip()
			if not self.item['Building_name']:
				self.item['Building_name'] = re.findall(' in (.*)?\s',build)
				if self.item['Building_name']:
					self.item['Building_name'] = self.item['Building_name'][0].strip()
		if not self.item['Building_name']:
			self.item['Building_name'] = 'None'

		value = response.xpath('//ul[@id="PropertyAttributes"]/li/span/text()').extract()
		if ' rent ' in conf:
			self.item['txn_type'] = 'Rent'
		if ' sale ' in conf:
			try:
				self.item['txn_type'] = [s.split(' ')[0] for s in value if ' Property' in s][0]
			except:
				self.item['txn_type'] = 'Sale'
			if 'ew' in self.item['txn_type']:
				self.item['txn_type'] = 'Sale'

		price = response.xpath('//div[@id="PropertyPrice"]/text()').extract()[-1].strip()
		if 'ale' in self.item['txn_type']:
			if 'lakh' in price:
				price = price.split(' lakh')[0]
				if (not '-' in price):
					self.item['Selling_price'] = str(float(price.split(' ')[0])*100000)
				elif ('-' in price):
					self.item['Selling_price'] = str(float(price.split(' ')[-1])*100000)
			if 'crore' in price:
				price = price.split(' crore')[0]
				if (not '-' in price):
					self.item['Selling_price'] = str(float(price.split(' ')[0])*10000000)
				elif ('-' in price):
					self.item['Selling_price'] = str(float(price.split(' ')[-1])*10000000)
		if 'Rent' in self.item['txn_type']:
			if ',' in price:
				self.item['Monthly_Rent'] = price.replace(',','')
			if 'lakh' in price:
				price = price.split(' lakh')[0]
				if (not '-' in price):
					self.item['Monthly_Rent'] = str(float(price.split(' ')[0])*100000)
				elif ('-' in price):
					self.item['Monthly_Rent'] = str(float(price.split(' ')[-1])*100000)
			if 'crore' in price:
				price = price.split(' crore')[0]
				if (not '-' in price):
					self.item['Monthly_Rent'] = str(float(price.split(' ')[0])*10000000)
				elif ('-' in price):
					self.item['Monthly_Rent'] = str(float(price.split(' ')[-1])*10000000)

		try:
			poss = [pos for pos in value if ('Immediate' in pos) or (('Within' in pos) and ('Year' in pos)) or (('Within' in pos) and ('Month' in pos))][0]
		except:
			poss = 'None'
		if 'Immediate' in poss:
			self.item['Possession'] = dt.today().strftime('%m/%d/%Y %H:%M:%S')
			self.item['Status'] = 'Ready to move'
		if (('Within' in poss) and ('Year' in poss)):
			poss1 = int(poss.replace('Within ','').split(' Year')[0])
			self.item['Possession'] = (dt.today()+relativedelta(years=poss1)).strftime('%m/%d/%Y %H:%M:%S')
			self.item['Status'] = 'Under Construction'
		if (('Within' in poss) and ('Month' in poss)):
			poss1 = int(poss.replace('Within ','').split(' Month')[0])
			self.item['Possession'] = (dt.today()+relativedelta(months=poss1)).strftime('%m/%d/%Y %H:%M:%S')
			self.item['Status'] = 'Under Construction'

		try:
			self.item['Bua_sqft'] = response.xpath('//span[@class="areaUnit downArrow"]/text()').extract_first().split(' ')[0]
		except:
			self.item['Bua_sqft'] = '0'

		if 'esale' in self.item['txn_type']:
			try:
				self.item['age'] = [age for age in value if 'Years' in age][0]
			except:
				self.item['age'] = 'None'
			if not self.item['age']:
				self.item['age'] = 'None'

		self.item['scraped_time'] = dt.now().strftime('%m/%d/%Y %H:%M:%S')

		if (((not self.item['Monthly_Rent'] == '0') and (not self.item['Bua_sqft']=='0') and (not self.item['Building_name']=='None') and (not self.item['lat']=='0')) or ((not self.item['Selling_price'] == '0') and (not self.item['Bua_sqft']=='0') and (not self.item['Building_name']=='None') and (not self.item['lat']=='0')) or ((not self.item['price_per_sqft'] == '0') and (not self.item['Bua_sqft']=='0') and (not self.item['Building_name']=='None') and (not self.item['lat']=='0'))):
			self.item['quality4'] = 1
		elif (((not self.item['price_per_sqft'] == '0') and (not self.item['Building_name']=='None') and (not self.item['lat']=='0')) or ((not self.item['Selling_price'] == '0') and (not self.item['Bua_sqft']=='0') and (not self.item['lat']=='0')) or ((not self.item['Monthly_Rent'] == '0') and (not self.item['Bua_sqft']=='0') and (not self.item['lat']=='0')) or ((not self.item['Selling_price'] == '0') and (not self.item['Bua_sqft']=='0') and (not self.item['Building_name']=='None')) or ((not self.item['Monthly_Rent'] == '0') and (not self.item['Bua_sqft']=='0') and (not self.item['Building_name']=='None'))):
			self.item['quality4'] = 0.5
		else:
			self.item['quality4'] = 0
		if ((not self.item['Building_name'] == 'None') and (not self.item['listing_date'] == '0') and (not self.item['txn_type'] == 'None') and (not self.item['property_type'] == 'None') and ((not self.item['Selling_price'] == '0') or (not self.item['Monthly_Rent'] == '0'))):
			self.item['quality1'] = 1
		else:
			self.item['quality1'] = 0

		if ((not self.item['Launch_date'] == '0') or (not self.item['Possession'] == '0')):
			self.item['quality2'] = 1
		else:
			self.item['quality2'] = 0

		if ((not self.item['mobile_lister'] == 'None') or (not self.item['listing_by'] == 'None') or (not self.item['name_lister'] == 'None')):
			self.item['quality3'] = 1
		else:
			self.item['quality3'] = 0
		
		yield self.item