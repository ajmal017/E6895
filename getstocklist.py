import urllib
from yahoo_finance import Share
import time

urllib.urlretrieve('ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt', 'nasdaqlisted.txt')

line = []
with open('nasdaqlisted.txt','r') as f:
	lines = f.read().split("\r\n")
	header = lines[0]
	lines = lines[1:-2] #ignore last two lines
		
print "Number of stock symbols", len(lines)
stock_symbols = map(lambda x:(x.split('|')[0],x.split('|')[1]), lines)
print stock_symbols 
	
#stock = Share('GOOG')
#print "50 day moving avg = ",stock.get_50day_moving_avg()
#print "200 day moving avg = ",stock.get_200day_moving_avg()
#print "Price earnings ratio = ",stock.get_price_earnings_ratio()
#print "Price earnings growth ratio = ",stock.get_price_earnings_growth_ratio()

with open("data/PE_ratio.txt","w") as fw:
	for sym,comp in stock_symbols:
		time.sleep(0.01)
		stock = Share(sym)
		print sym,comp
		while True:
			try:
				PE_ratio = stock.get_price_earnings_ratio()
				break;
			except e:
				print "Retrying stock", sym
				time.sleep(1)

		if PE_ratio != None and PE_ratio > 0:
			fw.write(sym+":"+comp+":"+str(PE_ratio)+"\n")


with open("data/PE_growth_ratio.txt","w") as fw:
	for sym,comp in stock_symbols:
		time.sleep(0.01)
		stock = Share(sym)
		print sym, comp
		while True:
			try: 
				PEG_ratio = stock.get_price_earnings_growth_ratio()
				break;
			except e:
				print "Retrying stock", sym
				time.sleep(1)
		
		if PEG_ratio != None and PEG_ratio > 0:
			fw.write(sym+":"+comp+":"+str(PEG_ratio)+"\n")

	
