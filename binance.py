#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
 
 
import json
import time

import urllib3

class binance():
	
	def __init__(self):
		self.ticker = {}
		self.ticker_old = {}
		self.ma7=[]
		self.ma77=[]
		self.ma251=[]
		
		self.tabticker = []
		
	def checkTicker(self):
		url = "https://api.binance.com/api/v1/ticker/24hr"
		
		urllib3.disable_warnings()
		http = urllib3.PoolManager()
		try:
			r = http.request('GET', url)
		except Exception:
			print('Connexion error, waiting 60s')
			time.sleep(60)

		self.ticker_old = self.ticker
		self.ticker = json.loads(r.data.decode('utf-8'))
		
		return self.ticker
	
	#Check for each coin the information and return a tab of ticker
	def checkAllInfoValues(self, period):
		tabticker = []
	
		for s in self.ticker:
				if "BTC" in s['symbol']:
					res = {}
					res['symbol'] = str(s['symbol'])
					url = "https://api.binance.com/api/v1/klines?symbol=" + str(s['symbol']) + "&interval=" + period +"&limit=252"
					urllib3.disable_warnings()
					http = urllib3.PoolManager()
					try:
						r = http.request('GET', url)
					except Exception:
						print('Connexion error, waiting 60s')
						time.sleep(60)

					try:
						res['values'] = json.loads(r.data.decode('utf-8'))
						tabticker.append(res)
					except:
						print("/!\ JSON empty")
						
		self.tabticker = tabticker
		
		return tabticker
	
	
	
	def getListSymbol(self, ticker):
		symbol = []
		for s in ticker:
			if s['symbol'] != '123456':
				if "BTC" in s['symbol']:
					symbol.append(s['symbol'])
		
		return symbol
	
	#Check for new symbol on the exchange
	def getNewSymbol(self):
		symbol = []
		tickerold = []
		newsymbol = []
		i = 0 # check
		symbol = self.getListSymbol(self.ticker)
		symbolold = self.getListSymbol(self.ticker_old)
		if len(symbolold) != 0:
			for t in symbol:
				i = 0
				for told in symbolold:
					if t == told:
						i = 1
						break
				if i == 0:
					newsymbol.append(t)

		return	newsymbol	
				


		
		
		
		
		
		
