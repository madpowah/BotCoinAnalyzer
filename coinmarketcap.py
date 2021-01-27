#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


import json
import time

import urllib3
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

class coinmarketcap():
	
	def __init__(self):
		#new data
		self.total_market_cap_eur = 0
		self.total_24h_volume_eur = 0
		self.bitcoin_percentage_of_market_cap = 0
		self.last_updated = 0
		
		self.trend = 0
		
		#old data to compare
		self.total_market_cap_eur_old = 0
		self.total_24h_volume_eur_old = 0
		self.bitcoin_percentage_of_market_cap_old = 0
		self.last_updated_old = 0
		
		self.tickermarket = {}
		self.tickermarket_old = {}
		
## Check global data from coinmarketcap
	def checkGlobal(self):
		url = 'https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest'

		headers = {
			'Accepts': 'application/json',
			'X-CMC_PRO_API_KEY': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX',
		}

		session = Session()
		session.headers.update(headers)

		try:
			response = session.get(url)
			globalmarket = json.loads(response.text)
			print(globalmarket)
		except (ConnectionError, Timeout, TooManyRedirects) as e:
			time.sleep(60)
			print(e)
		
		self.total_market_cap_eur_old = self.total_market_cap_eur
		self.total_24h_volume_eur_old = self.total_24h_volume_eur
		self.bitcoin_percentage_of_market_cap_old = self.bitcoin_percentage_of_market_cap
		self.last_updated_old = self.last_updated
		
		self.total_market_cap_eur = globalmarket['data']['quote']['USD']['total_market_cap']
		self.total_24h_volume_eur = globalmarket['data']['quote']['USD']['total_volume_24h']
		self.bitcoin_percentage_of_market_cap = globalmarket['data']['btc_dominance']
		self.last_updated = globalmarket['data']['last_updated']
		
		return 0

## Analyze total market cap to see the market trend
	def analyze_total_market_cap_eur(self):
		res = 0
		if self.total_market_cap_eur_old != 0:
			#val = 100 - (self.total_market_cap_eur / self.total_market_cap_eur_old) * 100
			val = (self.total_market_cap_eur - self.total_market_cap_eur_old) / self.total_market_cap_eur * 100
			if val < -2:
				res = 1
			else:
				if val > 2:
					res = -1
					
			self.trend = val
	
		return res
		
## Analyze BTC dominance to see the BTC trend
	def analyze_bitcoin_percentage_of_market_cap(self):
		res = 0
		if self.bitcoin_percentage_of_market_cap_old != 0:
			if (self.bitcoin_percentage_of_market_cap_old - self.bitcoin_percentage_of_market_cap) > 1:
				res = -1
			else:
				if (self.bitcoin_percentage_of_market_cap_old - self.bitcoin_percentage_of_market_cap) < -1:
					res = 1
			
		return res
			
	def get_bitcoin_percentage_of_market_cap(self):
		return self.bitcoin_percentage_of_market_cap
			
	def get_trend(self):
		return round(self.trend, 2)
		
	def get_marketcap(self):
		return int(self.total_market_cap_eur)
			
## Check Ticker data from coinmarketcap	
	def checkTicker(self):
		
		url = "https://api.coinmarketcap.com/v1/ticker/?convert=EUR"
		
		urllib3.disable_warnings()
		http = urllib3.PoolManager()
		r = http.request('GET', url)
		self.tickermarket_old = self.tickermarket
		self.tickermarket = json.loads(r.data.decode('utf-8'))
		
		return 0


## Check Pump and Dump price (+-5%)
	def checkPriceChange(self):
		pump = []
		dump = []
		for v in self.tickermarket:
			
			if float(v['percent_change_1h']) > 5:
				for w in self.tickermarket_old:
					if w['symbol'] == v['symbol']:
						if float(w['percent_change_1h']) < 5:
							pump.append(v)
							break
			else :
				if float(v['percent_change_1h']) < -5:
					for w in self.tickermarket_old:
						if w['symbol'] == v['symbol']:
							if float(w['percent_change_1h']) > -5:
								dump.append(v)
								break
								
		return pump,dump	
		
## Check Rank change fo a currency
	def checkRankChange(self):
		rank = []
		oldrank = []
		i = -1

		for v in self.tickermarket:
			i = i+1
			for w in self.tickermarket_old:
				if w['symbol'] == v['symbol']:
					if int(v['rank']) > int(w['rank']):
						if int(v['rank']) < 20:

							rank.append(v)
							oldrank.append(w)
							break
		return rank, oldrank
		
