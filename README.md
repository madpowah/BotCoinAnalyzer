# BotCoinAnalyzer
A telegram bot which analyze Binance crypto market and send signals.
Demo on Telegram, channel Coin Analyzer

Create the bot on telegram and a channel and change line 24 of coinanalyse.py with the good values :
url = "https://api.telegram.org/bot123456789:XXXXXXXXXXXXXXXXx/sendMessage?parse_mode=Markdown&chat_id=-123456789&text=" + txt

Create a KEY on coinmarketcap (it's free) and put it on coinmarketcap.py line 39 :
'X-CMC_PRO_API_KEY': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX',

Launch coinanalyze.py
