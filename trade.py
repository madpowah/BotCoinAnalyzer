#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import talib
import numpy as np

class trade():
	
	def __init__(self):
		self.capital = 1
		self.startcapital = self.capital
		self.amountbytrade = 0.1
		self.trade = []		#{'symbol' : symbol, 'type' : 1, 'nb' : nbbuy, 'price' : price, 'stoploss' : stoploss, 'profit' : profit}
		self.fee = 0.1
		self.nbtradetodo = 10
		self.nbtradeopen = 0
		self.nbtradedone = 0
		self.end = 0
		
		
	def buysell(self, buysell, symbol, price):
		tr = {}
		msg = ""
		lastprice = 0
		if (buysell == 1) and (self.nbtradeopen < self.nbtradetodo) :
			
			lasttype = 2
			nbsell = 0.0
			
			#Si on a déjà un achat sur ce coin on n'achete pas
			for t in self.trade:
				if (t['symbol'] == symbol):
					lasttype = t['type']
					lastprice = t['price']
					nbsell = t['nb']
			if lasttype == 2:
				#Sil reste du capital
				if self.capital > 0.01:
					amount = self.amountbytrade
					#Si on a plus que le cout d'un trade
					if self.amountbytrade > self.capital:
						amount = self.capital
					
					nbbuy = amount / float(price)
					
					stoploss = float(price) - ((float(price) * 5) / 100)
		
					if lastprice != 0:
						profit = (float(nbsell) * float(lastprice) - float(nbbuy) * float(price)) / (float(nbsell) * float(lastprice)) * 100
					else :
						profit = 0
					
					tr = {'symbol' : symbol, 'type' : 1, 'nb' : nbbuy, 'price' : price, 'stoploss' : stoploss, 'profit' : profit}
					print(str(price) + " - STOPLOSS : " + str(stoploss))
					self.trade.append(tr)
					
					#On met a jour le capital avec l'achat
					self.capital = self.capital - (float(nbbuy) * float(price))
					self.nbtradeopen = self.nbtradeopen + 1
					
					msg = self.printBuySell(tr)
			
		if buysell == -1:
			lasttype = 2
			nbbuy = 0.0
			lastprice = 0
			#On recherche le dernier achat pour voir si on vend et le nombre qu'on a
			for t in self.trade:
				if (t['symbol'] == symbol):
					lasttype = t['type']
					lastprice = t['price']
					nbbuy = t['nb']
			if lasttype == 1 :

				#profit = (float(nbbuy) * float(lastprice) - float(nbbuy) * float(price)) / (float(nbbuy) * float(lastprice)) * 100
				profit = (100 * (float(nbbuy) * float(price)) / (float(nbbuy) * float(lastprice))) - 100
				tr = {'symbol' : symbol, 'type' : 2, 'nb' : nbbuy, 'price' : price, 'stoploss' : 0, 'profit' : profit}
				self.trade.append(tr)
				
				#On met a jour le capital avec l'achat
				self.capital = self.capital + (float(nbbuy) * float(price))
				self.nbtradedone = self.nbtradedone + 1
				
				msg = self.printBuySell(tr)
		
		
		return tr,msg

	def checkEndTrade(self):
		msg = ""
		if (self.nbtradedone == self.nbtradetodo) and (self.end == 0):
			msg =  "End of trading Session !\n"
			msg = msg + "Summary :"
			msg = msg + "- Capital at start : 1 Bitcoin\n"
			msg = msg + "- Capital at end : " + str(self.capital) + " Bitcoin\n"
			msg = msg + "- Nb trade done : " + str(self.nbtradedone) + "\n"
			self.end = 1
			msg = msg + "- Trades : : "
			listcoin = []
			for t in self.trade:
				coin = t['symbol']
				res = 0
				for l in listcoin:
					if coin == l:
						res = 1
				if res != 1:
					listcoin.append(coin)
			for c in listcoin:
				for t in self.trade:
					if c == t['symbol']:
						if t['type'] == 1:
							msg = msg + "BUY "
						else:
							msg = msg + "SELL "
							
						msg = msg + t['symbol'] + " " + str(t['nb']) + " at " + str(t['price']) + "Bitcoin. Profit : " + str(t['profit']) + "\n"
						print(msg)
						
				
			return 1, msg
		
		return 0,msg
		
	def summaryTrade(self):
		listcoin = []
		msg = "Summary :"
		msg = msg + "- Capital at start : " + str(self.startcapital) + " Bitcoin\n"
		msg = msg + "- Actual apital : " + str(self.capital) + " Bitcoin\n"
		msg = msg + "- Nb trade to do : " + str(self.nbtradetodo) + "\n"
		msg = msg + "- Nb trade done : " + str(self.nbtradedone) + "\n"
		msg = msg + "- Nb trade opened : " + str(self.nbtradeopen) + "\n"
		msg = msg + "-Trades : \n"
		for t in self.trade:
			coin = t['symbol']
			res = 0
			for l in listcoin:
				if coin == l:
					res = 1
			if res != 1:
				listcoin.append(coin)
		for c in listcoin:
			for t in self.trade:
				if c == t['symbol']:
					if t['type'] == 1:
						msg = msg + "BUY "
					else:
						msg = msg + "SELL "
						
					msg = msg + t['symbol'] + " " + str(t['nb']) + " at " + str(t['price']) + "Bitcoin. Profit : " + str(t['profit']) + "\n"
						

		return msg
	
	
	#### STOPLOSS #####
	def stopLoss(self, coin):
		stoploss = 0
		price = coin.getLastPrice()
		for tr in self.trade:
			if tr['symbol'] == coin.getSymbol() and tr['type'] == 1:
				stoploss = tr['stoploss']
				
		if price < stoploss:
			self.buysell(2, coin.getSymbol(), price)
			return 1
		
		return 0

	def printBuySell(self, buysell):
		msg = ""
		if buysell['type'] == 1:
			msg = msg + "TRADE >> Buy " + str(buysell['nb']) + ' ' + str(buysell['symbol']) + ' at ' + str(buysell['price'])
		if buysell['type'] == 2:
			msg = msg +  "TRADE >> SELL " + str(buysell['nb']) + ' ' + str(buysell['symbol']) + ' at ' + str(buysell['price'])
			
		msg = msg + "\nCapital :" + str(self.getCapital()) + ' Bitcoin'
		
		return msg
		
	def getCapital(self):
		return self.capital
