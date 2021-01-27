#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import talib
import numpy as np

class coin():
	def __init__(self, symbol):
		self.data = {}
		self.data['symbol'] = symbol
		self.lastValues = [] # Last candle values
		self.period = ['30m', '1h', '4h', '1d']
		self.PRSsurveillance = {}
		for p in self.period:
			self.data['macd' + p] = 100.0
			self.data['macdold' + p] = 100.0
			self.data['rsi' + p] = 50.0
			self.data['rsiold' + p] = 50.0
			self.data['rsidiv' + p] = 1
			self.data['rsidivold' + p] = 1
			self.data['cci' + p] = 100.0
			self.data['cciold' + p] = 100.0
			self.PRSsurveillance[p] = {'type' : 0}
			self.data['ma7' + p] = 0.0
			self.data['ma7old' + p] = 0.0
			self.data['ma77' + p] = 0.0
			self.data['ma77old' + p] = 0.0
			self.data['adx' + p] = 0
			self.data['cloud' + p] = 1
			self.data['ema' + p] = 0

	def getLastPrice(self):
		return self.lastValues[-1][4]
		
	def getSymbol(self):
		return self.data['symbol']
		
	def getSymbol(self):
		return self.data['symbol']
		
	def setValues(self, info):
		self.lastValues = info['values']
	
	def checkSigne(self, value):
		if value >= 0:
			return 1
		else: 
			return -1
		
	### Check MACD cross
	# if Bullish, return 1
	# if Bearish, return -1
	# if no change, return 0
	def macdAlert(self, period):
		fastperiod=12
		slowperiod=26
		signalperiod=9
		closes = []
		
		#We save the old value to compare and check a trend change
		self.data['macdold' + period] = self.data['macd' + period]
		for x in self.lastValues:
			closes.append(float(x[4]))
			
		nparray = np.asarray(closes)
		
		macd, macdsignal, macdhist = talib.MACD(nparray, fastperiod, slowperiod, signalperiod)
		self.data['macd' + period] = macd[-1] - macdsignal[-1] #if > 0, bullish, else bearish
		#print "MACD + " + self.data['symbol'] + " = " + str(self.data['macd'])
		
		#Si ce n'est pas le 1er lancement
		if self.data['macdold' + period] == 100.0:
			return 0, self.getLastPrice()
		if self.checkSigne(self.data['macd' + period]) != self.checkSigne(self.data['macdold' + period]):
			if self.checkSigne(self.data['macd' + period]) == 1:
				print(self.getSymbol() + " : macd = " + str(self.data['macd' + period]) + " | " + "macdold = " + str(self.data['macdold' + period]))
				self.PRSsurveillance[period] = {'type' : 1, 'rsi' : self.data['rsi' + period]} # On ajoute le token à la surveillance RSI en mode Bullish
				return 1, self.getLastPrice()
			else:
				print(self.getSymbol() + " : macd = " + str(self.data['macd' + period]) + " | " + "macdold = " + str(self.data['macdold' + period]))
				self.PRSsurveillance[period] = {'type' : -1, 'rsi' : self.data['rsi' + period]} # On ajoute le token à la surveillance RSI en mode Bearish
				return -1, self.getLastPrice()
		else:
			return 0, self.getLastPrice()
			

		
	### Check RSI signal
	# if time to buy, return 1
	# if time to sell, return -1
	# else, return 0
	def rsiAlert(self, period):
		rsiperiod=14
		closes = []
		self.data['rsiold' + period] = self.data['rsi' + period]
		
		for x in self.lastValues:
			closes.append(float(x[4]))
			
		nparray = np.asarray(closes)
		rsi = talib.RSI(nparray, rsiperiod)
		self.data['rsi' + period] = rsi[-1]
		
		if self.data['rsi' + period] < 30:
			if self.data['rsiold' + period] > 30:
				print("RSI : " + str(self.data['rsi' + period]))
				return 1
		if self.data['rsi' + period] > 70:
			if self.data['rsiold' + period] < 70:
				print("RSI : " + str(self.data['rsi' + period]))
				return -1
		
		return 0
			
			
			
	### Pivot Reversal Strategy
	# If MACD cross then mise en surveillance
	# Every 5mn, check if RSI + - 5 Then PRS Alert
	# Return 1 if PRS gives a BUY Signal
	# Return -1 if PRS gives a SELL Signal
	def prsAlert(self, period):
		if self.PRSsurveillance[period]['type'] == 1:
			rsitest = self.PRSsurveillance[period]['rsi'] + 5
			if self.data['rsi' + period] > rsitest:
				self.PRSsurveillance[period]['type'] = 0
				return 1, self.getLastPrice()
		if self.PRSsurveillance[period]['type'] == -1:
			rsitest = self.PRSsurveillance[period]['rsi'] - 5
			if self.data['rsi' + period] < rsitest:
				self.PRSsurveillance[period]['type'] = 0
				return -1, self.getLastPrice()
				
		return 0, 0
		
	### ADX / DI Alert
	# If ADX > 25 and DI+ > DI- and ADX => BUY
	# If ADX > 25 and DI- > DI+ and ADX => SELL
	#long_adx = ADX > 25 and ADX[1] < 25 and DIPlus > ADX and DIPlus > DIMinus ? true : false
	#short_adx = ADX > 25 and ADX[1] < 25 and DIMinus > ADX and DIMinus > DIPlus ? true : false
	def adxAlert(self, period):
		closes = []
		highs = []
		lows = []
		
		for x in self.lastValues:
			closes.append(float(x[4]))
			highs.append(float(x[2]))
			lows.append(float(x[3]))
			
		nparraycloses = np.asarray(closes)
		nparrayhighs = np.asarray(highs)
		nparraylows = np.asarray(lows)
		
		diminus = talib.MINUS_DM(nparrayhighs, nparraylows, timeperiod=14)
		diplus = talib.PLUS_DM(nparrayhighs, nparraylows, timeperiod=14)
		adx = talib.ADX(nparrayhighs, nparraylows, nparraycloses, timeperiod=14)
		
		if (adx[-1] > 25) and (diplus[-1] > adx[-1]) and (diplus[-1] > diminus[-1]) and (self.data['adx' + period] == 0):
			self.data['adx' + period] = 1
			return 1, self.getLastPrice()
		if (adx[-1] > 25) and (diminus[-1] > adx[-1]) and (diminus[-1] > diplus[-1]) and (self.data['adx' + period] == 0):
			self.data['adx' + period] = -1
			return -1, self.getLastPrice()
		
		if adx[-1] < 25:
			self.data['adx' + period] = 0
			
		return 0, 0
		
	### CCI / RSI Alert
	# long_cci = cci > 100 and rsi < 70 and cci[1] < 100
	# short_cci = cci < -100 and rsi < 60 and rsi > 30 and cci[1] > -100

	def cciAlert(self, period):
		closes = []
		highs = []
		lows = []
		
		self.data['cciold' + period] = self.data['cci' + period]
		
		for x in self.lastValues:
			closes.append(float(x[4]))
			highs.append(float(x[2]))
			lows.append(float(x[3]))
			
		nparraycloses = np.asarray(closes)
		nparrayhighs = np.asarray(highs)
		nparraylows = np.asarray(lows)

		cci = talib.CCI(nparrayhighs, nparraylows, nparraycloses, timeperiod=20)
		
		if (cci[-1] > 100) and (self.data['rsi' + period] < 70) and (self.data['cciold' + period] == 0):
			self.data['cci' + period] = 1
			return 1, self.getLastPrice()
		if (cci[-1] < -100) and (self.data['rsi' + period] > 60) and (self.data['cciold' + period]  == 0):
			self.data['cci' + period] = 1
			return 1, self.getLastPrice()
		
		if (self.data['cci' + period] == 1) and (cci[-1] < 100):
			self.data['cci' + period] = 0
		if (self.data['cci' + period] == -1) and (cci[-1] > -100):
			self.data['cci' + period] = 0
			
		return 0, 0
		
		
	### RSI Divergence
	# res = high > previousprice and rsi < rsi[previousrsi] and rsi > 50 ? 1 : 0

	def rsiDivAlert(self, period):
		closes = []
		highs = []
		
		self.data['rsidivold' + period] = self.data['rsidiv' + period]
		
		for x in self.lastValues:
			closes.append(float(x[4]))
			highs.append(float(x[2]))
			
		nparraycloses = np.asarray(closes)

		rsi = talib.RSI(nparraycloses, timeperiod=14)
		
		previousrsi = 0
		if len(rsi) > 22:
			if (rsi[-1] < rsi[-2]) and (rsi[-2] > rsi[-3]):
				trigger = 0
				for i in range(2, 20):
					if rsi[-1 - i] > rsi[0-i]:
						trigger = 1
					if trigger == 1:
						if rsi[-1 - i] < rsi[0-i]:
							previousrsi = -1 - i
							break
							
			previousprice = highs[previousrsi]
			
			if previousprice < highs[-1] and rsi[-1] < rsi[previousrsi] and rsi[-1] > 50 and self.data['rsidiv' + period] != 1:
				self.data['rsidiv' + period] = 1
				return -1, self.getLastPrice()
				
			if previousprice > highs[-1] or rsi[-1] > rsi[previousrsi] or rsi[-1] < 50:
				self.data['rsidiv' + period] = 0
			
		return 0, 0
	
	#Calcul MA7/MA77/MA251. Si MA7 passe au dessus de MA77 avec MA7 au dessus de MA251, alors bon point d'entrée pour achat

	def nightouAlert(self, period):
		res = []
		closes = []
		ma7 = 0.0
		ma77 = 0.0
		ma251 = 0.0
		
		#########
		#We calculate for the actual MA
		#MA7
		self.data['ma7old' + period] = self.data['ma7' + period]
		self.data['ma77old' + period] = self.data['ma77' + period]
		
		for x in self.lastValues:
			closes.append(float(x[4]))
			
		nparray = np.asarray(closes)
		ma7 = talib.MA(nparray, timeperiod=7, matype=0)
		ma77 = talib.MA(nparray, timeperiod=77, matype=0)
		ma251 = talib.MA(nparray, timeperiod=251, matype=0)
		
		self.data['ma7' + period] = ma7[-1]
		self.data['ma77' + period] = ma77[-1]
		self.data['ma251' + period] = ma251[-1]
		
		##CALCUL for ALERT
		if self.data['ma7' + period] > self.data['ma77' + period]:
			if self.data['ma251' + period] < self.data['ma7' + period]:
				if self.data['ma7old' + period] < self.data['ma77old' + period]:
					if self.PRSsurveillance[period]['type'] == 1:
						return 1, self.getLastPrice()
	
		return 0, 0

	def cloudStrategy(self, period):
		macd, macdsignal, macdhist = self.getMACD(period)
		rsi = self.getRSI(period)

		long_macd = 0
		short_macd = 0
		bull_macd = 0
		long_rsi = 0
		short_rsi = 0
		#resistance, support = self.getSupport(period)
		
		if macd[-1] > 0 and macd[-1] > macd[-2]:
			long_macd = 1
		if macd[-1] < 0:
			short_macd = 1
		if macd[-1] > macdsignal[-1]:
			bull_macd = 1
		if rsi[-1] > 41.6 and rsi[-1] < 60:
			long_rsi = 1
		if rsi[-1] < 41.6 and rsi[-2] > 41.6:
			short_rsi = 1
		
		if ((long_macd == 1 and bull_macd == 1 and long_rsi == 1) or rsi[-1] < 20) and self.data['cloud' + period] == 0:
			self.data['cloud' + period] = 1
			return 1, self.getLastPrice()
		if short_rsi == 1 and self.data['cloud' + period] == 1:
			self.data['cloud' + period] = 0
			return -1, self.getLastPrice()
			
		return 0, 0
		
	def emaStrategy(self, period):

		closes = []
		
		for x in self.lastValues:
			closes.append(float(x[4]))
			
		nparray = np.asarray(closes)
		ema8 = talib.EMA(nparray, timeperiod=8)
		ema13 = talib.EMA(nparray, timeperiod=13)
		ema21 = talib.EMA(nparray, timeperiod=21)
		ema55 = talib.EMA(nparray, timeperiod=55)

		if (ema55[-1] < ema8[-1] and ema55[-1] < ema13[-1] and ema55[-1] < ema21[-1]) and (ema55[-2] > ema8[-2] or ema55[-2] > ema13[-2] or ema55[-2] > ema21[-2]) and self.data['ema' + period] == 1:
			self.data['ema' + period] = 0
			return 1, self.getLastPrice()
		if (ema55[-1] > ema8[-1] and ema55[-1] > ema13[-1] and ema55[-1] > ema21[-1]) and (ema55[-2] < ema8[-2] or ema55[-2] < ema13[-2] or ema55[-2] < ema21[-2]) and self.data['ema' + period] == 0:
			self.data['ema' + period] = 1
			return -1, self.getLastPrice()
			
		return 0,0
			
	def getMACD(self, period):
		fastperiod=12
		slowperiod=26
		signalperiod=9
		closes = []
		
		for x in self.lastValues:
			closes.append(float(x[4]))
			
		nparray = np.asarray(closes)
		
		macd, macdsignal, macdhist = talib.MACD(nparray, fastperiod, slowperiod, signalperiod)
		
		return macd, macdsignal, macdhist
		
	def getRSI(self, period):
		rsiperiod=14
		closes = []
		self.data['rsiold' + period] = self.data['rsi' + period]
		
		for x in self.lastValues:
			closes.append(float(x[4]))
			
		nparray = np.asarray(closes)
		rsi = talib.RSI(nparray, rsiperiod)
		
		return rsi
		
	def getSupport(self, period):
		highs = []
		lows = []
		for x in self.lastValues:
			highs.append(float(x[2]))
			lows.append(float(x[3]))
		
		high = 0
		low = 0
		nbcandle = 10 #adjust to set the sensitivity
		for a in range((-1 - nbcandle), -1):
			if highs[a] > high:
				high = highs[a]
			if lows[a] < low:
				low = lows[a]
		
		return high, low
		
