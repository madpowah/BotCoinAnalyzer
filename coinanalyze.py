#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import time
from datetime import datetime, date, timedelta
import urllib3
from coinmarketcap import coinmarketcap
from binance import binance
from coin import coin
from trade import trade
import numpy as np
import importlib
import sys
importlib.reload(sys)
#reload(sys)


#### Send To Coin ANalyzer Channel on Telegram
def sendMessageTelegram(msg):
	
	#We replace %n by %0A for Telegram
	txt = msg.replace("\n", "%0A")
	url = "https://api.telegram.org/bot123456789:XXXXXXXXXXXXXXXXx/sendMessage?parse_mode=Markdown&chat_id=-123456789&text=" + txt
	urllib3.disable_warnings()
	http = urllib3.PoolManager()
	r = http.request('GET', url)
	
	return 0

#### Return text for market trend
def printcheckmarket(market, checkmarket):
	res = ""
	res = "* Total marketcap : " + str(market.get_marketcap()) + "*\n"
	if checkmarket == 0:
		res = res + "* Normal Market : (" + str(market.get_trend()) + "%)*"
	else:
		if checkmarket == -1:
			if market.get_trend() > 3:
				res = res + "* /!\ /!\ REALLY BULLISH Market /!\ /!\ >> (" + str(market.get_trend()) + "%)*"
			else:
				res = res + "* BULLISH Market : (" + str(market.get_trend()) + "%)*"

		else:
			if checkmarket == 1:
				if market.get_trend() < -3:
					res = res + "* /!\ /!\ REALLY BEARISH Market /!\ /!\ >> (" + str(market.get_trend()) + "%)*"
				else:
					res = res + "* BEARISH Market : (" + str(market.get_trend()) + "%)*"
	return res
		
		
#### Return text for BTC domination		
def printbtcdominance(market, checkmarket):
	res = ""
	if checkmarket == 0:
		res = "* BTC dominance isn't moving : " + str(market.get_bitcoin_percentage_of_market_cap()) + "%*"
	else:
		if checkmarket == 1:
			res = "* BTC dominance on fire : +" + str(market.get_bitcoin_percentage_of_market_cap()) + "%*"
		else:
			if checkmarket == -1:
				res = "* BTC dominance dumping : " + str(market.get_bitcoin_percentage_of_market_cap()) + "%*"
	
	return res

#### Return Coin with 1h price change >5%
def printPumpDump(pump,dump):
	msg = ""
	if len(pump) != 0:
		msg = "* PUMP price (> 5%) : *\n"
		for v in pump:
			if float(v['percent_change_1h']) > 0:
				msg = msg + "\t* " + v['symbol'] + ' : +' + v['percent_change_1h'] + "%*\n"
				
	if len(dump) != 0:
		if msg != "":
			msg = msg + "\n"
		msg = msg + "* DUMP price (> 5%) :*\n"
		for v in dump:
			if float(v['percent_change_1h']) < 0:
				msg = msg + "\t* " + v['symbol'] + ' : ' + v['percent_change_1h'] + "%*\n"
			
	return msg

#### Return Coin with Rank change
## TODO : previous RANK
def printRankChange(rank,oldrank):
	msg = ""
	if len(rank) != 0:
		msg = "* RANK up :*\n"
		for v in rank:
			msg = msg + "\t" + v['symbol'] + ' - ' + v['rank'] + "\n"
			#msg = msg + "\t" + v[0] + ' - ' + v[2] + " >> " + v[1] + "\n"
				
			
	return msg
	
#### Return message for new coin on exchange
def printNewSymbol(symbol):
	msg = ""
	if len(symbol) != 0:
		msg = "* New Symbol on Binance :*\n"
		for s in symbol:
			msg = msg + "\t" + s + "\n"
	
	return msg

#Return MACD Alert msg
def printMACDAlert(symbol, macd, period, price):
	msg = "* MACD Signal (" + period +")*\n"
	if macd == 1:
		msg = msg + symbol + " Bullish signal on Binance at " + price + " sat\n"
	else:
		msg = msg + symbol + " Bearish signal on Binance at " + price + " sat\n"
		
	return msg
	
#Return RSI Alert msg
def printRSIAlert(symbol, rsi, period):
	msg = "* RSI Signal (" + period +")*\n"
	if rsi == 1:
		msg = msg + symbol + " Time to BUY on Binance\n"
	else:
		msg = msg + symbol + " Time to SELL on Binance\n"
		
	return msg

#Return RSI Divergence Alert msg
def printRSIDIVAlert(symbol, rsidiv, period, price):
	msg = "* RSI Divergence Signal (" + period +")*\n"
	
	if rsidiv == -1:
		msg = msg + symbol + " SELL Signal on Binance at " + price + " sat \n"
		
	return msg
	
	
### Return nightou alert
def printNightouAlert(symbol, period, price):

	msg = "* /!\\ Nightou Alert /!\\ (" + period +")* \n"
	msg = msg + "\t" + symbol + " Good entry at " + price + " sat ! \n"
				
	return msg


#Return Alert msg
def printAlert(strategy, symbol, ema, period, price):
	msg = "* " + strategy + " Signal (" + period +")*\n"

	if ema == 1:
		msg = msg + symbol + " BUY Signal on Binance at " + price + " sat \n"
	else:
		msg = msg + symbol + " SELL Signal on Binance at " + price + " sat \n"
		
	return msg

######## MAIN #####
def main():
	try:
		print("\n>> CoinAnalyze v0.7 by cloud <<\n\n")
		sendMessageTelegram("Coin Analyzer Bot v0.7 Started")
		
		##### TRADE MODULE#######
		trading = 0
		tr = trade()
		if trading == 1:
			print("Trading module : On")
			sendMessageTelegram("Trading module : On")
			end = 0
		else :
			print("Trading module : Off")
			sendMessageTelegram("Trading module : Off")
			
		#########################
		#We initialize the different timer
		timer1hnext = (datetime.now() + timedelta(seconds=3600)).hour
		timer20mnnext = (datetime.now() + timedelta(seconds=60))
		while (int(str(timer20mnnext.minute)) % 20) != 0:
			timer20mnnext = timer20mnnext + timedelta(seconds=60)
		market = coinmarketcap()
		binancecoin = binance()
		listcoin = []
		ticker = {}
		ticker = binancecoin.checkTicker()
					
		symbol = binancecoin.getListSymbol(ticker)
		
		#We create an object by coin
		for c in symbol:
			coinC = coin(c)
			listcoin.append(coinC)
			
		
		while True:
			time.sleep(1)
			timer = datetime.now()
			
			####### EVERY 1H ###############
			
			if timer.hour == timer1hnext:
				print(timer)
				
				if trading == 1:
					msg = tr.summaryTrade()
					print(msg)
					sendMessageTelegram(msg)
				timer1hnext = (datetime.now() + timedelta(seconds=3600)).hour

				### We check General coinmarketcap every 60mn
				
				market.checkGlobal()
				checkmarket = market.analyze_total_market_cap_eur()
				
				#Analyze Market
				msg = ""
				msg = msg + printcheckmarket(market, checkmarket)
				msg = msg + "\n"
				
				checkmarket = market.analyze_bitcoin_percentage_of_market_cap()
				msg = msg + printbtcdominance(market, checkmarket)
				
				print(msg)
				sendMessageTelegram(msg)
				msg = ""
			
				
			####### EVERY 20mn ###############
			## New Symbol check
			timer20mn = datetime.now()
			period = ['1h', '4h', '1d']

			if ((int(timer20mn.minute) % 20) == 0) and (timer20mnnext.minute == timer20mn.minute):
			#if 1 == 1:
				if trading == 1:
					period = ['1h', '4h', '1d']
				timer20mnnext = (datetime.now() + timedelta(seconds=12000))			
				####### ACTION ###################
				for p in period:
					
					msg = ""
					
					#On récupère les infos de chaque coin sur une période de 252 et on les ajoute à chaque coin pour gérer les alertes
					listAllValues = []
					listAllValues = binancecoin.checkAllInfoValues(p)

					for c in listAllValues:
						for x in listcoin:
							end, msg = tr.checkEndTrade()
				
							
							if end == 1:
								print(msg)
								sendMessageTelegram(msg)
								trading = 0
								period = ['4h', '1d']
							if c['symbol'] == x.getSymbol():
								x.setValues(c)
								if trading == 1:
									stoploss = tr.stopLoss(x)
									if stoploss == 1:
										msg = "STOP LOSS (5%) for " + x.getSymbol() 
										print(msg)
										sendMessageTelegram(msg)
								
								if p != '1h':
									#RSI must be the first test to set RSI for the PRS test
									#RSI alert check
									rsi = x.rsiAlert(p)
									if rsi != 0:
										msg = printRSIAlert(x.getSymbol(), rsi, p)
										print(msg)
										#sendMessageTelegram(msg)
										msg = ""
										
									#RSI DIV Alert
									rsidiv, price = x.rsiDivAlert(p)
									if rsidiv != 0:
										msg = msg + printRSIDIVAlert(x.getSymbol(), rsidiv, p, price)
										print(msg)
										sendMessageTelegram(msg)
										msg = ""
										#if trading == 1:
										#	restrade,msg = tr.buysell(rsidiv, x.getSymbol(), price)
										#	print msg
										#	sendMessageTelegram(msg)
									
									#MACD alert check
									macd, price = x.macdAlert(p)
									if macd != 0:
										msg = printMACDAlert(x.getSymbol(), macd, p, price)
										print(msg)
										#sendMessageTelegram(msg)
										msg = ""
										
										
									#PRS Alert
									prs, price = x.prsAlert(p)
									if prs != 0:
										msg = printAlert("PRS", x.getSymbol(), prs, p, price)
										print(msg)
										#sendMessageTelegram(msg)
										msg = ""
										#if trading == 1:
										#	restrade,msg = tr.buysell(prs, x.getSymbol(), price)
										#	print msg
										#	sendMessageTelegram(msg)
					

									#Nightou Alert
									nightou, price = x.nightouAlert(p)
									if nightou != 0:
										msg = msg + printNightouAlert(x.getSymbol(), p, price)
										print(msg)
										sendMessageTelegram(msg)
										msg = ""
										if trading == 1:
											restrade,msg = tr.buysell(nightou, x.getSymbol(), price)
											print(msg)
											sendMessageTelegram(msg)
					
									#ADX Alert
									adx, price = x.adxAlert(p)
									if adx != 0:
										msg = msg + printAlert("ADX", x.getSymbol(), adx, p, price)
										print(msg)
										#sendMessageTelegram(msg)
										msg = ""
										#if trading == 1:
										#	restrade,msg = tr.buysell(adx, x.getSymbol(), price)
										#	print msg
										#	sendMessageTelegram(msg)
										
									#CCI Alert
									cci, price = x.cciAlert(p)
									if cci != 0:
										msg = msg + printAlert("CCI", x.getSymbol(), cci, p, price)
										print(msg)
										#sendMessageTelegram(msg)
										msg = ""
										#if trading == 1:
										#	restrade,msg = tr.buysell(cci, x.getSymbol(), price)
										#	print msg
										#	sendMessageTelegram(msg)
											
									#CLOUD Alert
									cloud, price = x.cloudStrategy(p)
									if cloud != 0:
										msg = msg + printAlert("CLOUD", x.getSymbol(), cloud, p, price)
										print(msg)
										sendMessageTelegram(msg)
										msg = ""
										if trading == 1:
											restrade,msg = tr.buysell(cloud, x.getSymbol(), price)
											print(msg)
											sendMessageTelegram(msg)
										
								#EMA Alert
								ema, price = x.emaStrategy(p)
								if ema != 0:
									msg = msg + printAlert("EMA", x.getSymbol(), ema, p, price)
									print(msg)
									sendMessageTelegram(msg)
									msg = ""
									if trading == 1:
										restrade,msg = tr.buysell(ema, x.getSymbol(), price)
										print(msg)
										sendMessageTelegram(msg)
				
				
				####### NEW SYMBOL #########
				ticker = binancecoin.checkTicker()
				newsymbol = []
				newsymbol = binancecoin.getNewSymbol()
				for c in newsymbol:
					coinC = coin(c)
					listcoin.append(coinC)
					
				msg = printNewSymbol(newsymbol)
				if msg != "":
					sendMessageTelegram(msg)
					print(msg)
				
			
	except (KeyboardInterrupt, SystemExit):
		sendMessageTelegram("Maintenance, I'll be back soon")
	return 0


if __name__ == '__main__':
	main()
