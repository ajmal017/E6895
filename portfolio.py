import sys
import time
import urllib2
import csv
import os
import numpy as np
from collections import defaultdict
from yahoo_finance import Share
from cvxopt import matrix, solvers

cached = True


def get_price_history(stocksymbol, startyear, endyear):
	price_data = defaultdict(list)

	if cached and os.path.exists("cache/"+stocksymbol+"_"+str(startyear)+"_"+str(endyear)):
		with open("cache/"+stocksymbol+"_"+str(startyear)+"_"+str(endyear),"r") as fr:
			firstline = True
			header = []
			for line in fr:
				values = []
				line = line.strip() 
				if line == "":
					continue
				if firstline:
					header = line.split(',')
					firstline = False
				else:
					values = line.split(',')
				for i in range(len(values)):
					price_data[header[i]].insert(0, values[i]) #the data is in descending order of days, insert at the beginning

	else:	
		"""
		url = 'http://ichart.yahoo.com/table.csv?s='
		url2 = "%s%s&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=m" %(url, stocksymbol, 0, 1, int(startyear), 11, 31, int(endyear)) # 0/1 => Jan 1, 11/31 => Dec 31
		response = ""
		retries = 0
		while True:
			try:	
				response = urllib2.urlopen(url2)
				break
			except e:
				retries += 1
				if retries == 3:
					print "Too many reties for " + url2
					sys.exit(1)
				time.sleep(1)
			
		reader = csv.DictReader(response)
		"""
		stock = Share(symbol)
		histdata = stock.get_historical(startyear+'-01-01',endyear+'-12-31') #Jan 1 of startyear through Dec 31 of endyear		

		firstline = True
		with open("cache/"+stocksymbol+"_"+str(startyear)+"_"+str(endyear),"w") as fw:
			header = ""
			for row in histdata:
				values = ""
				for key, value in row.iteritems():
					if firstline:
						header += key+","
					values += value+","			
					price_data[key].insert(0, value) # retrieved data is in the descending order of days, insert at the beginning
				if firstline:
					fw.write(header[:-1]+"\n")
					firstline = False
				fw.write(values[:-1]+"\n")
	
	return price_data

def returns(stocksymbol, startyear, endyear):
	price_dict = get_price_history(stocksymbol, startyear, endyear)
	prices = [float(x) for x in price_dict["Close"]]
	prices.insert(0,float(price_dict["Open"][0]))
 	prices = [ prices[i] for i in range(0,len(prices),12)]
	#Average return
 	ret = [(prices[i+1] - prices[i]) for i in range(len(prices)-1)]
	print prices
	return ret

def markwtz_opt(avg_ret,dim,cov_mat,exp_ret):
	#print np.shape(np.array(avg_ret)), np.shape(np.transpose(avg_ret)) 
	P = cov_mat
	q = matrix(np.zeros((dim,1)))
	G = matrix(np.concatenate((np.transpose(avg_ret),np.identity(dim)), axis=0))
        #print "G=", G
	h = matrix(np.concatenate((matrix([1.0])*exp_ret, np.zeros((dim,1))), axis=0))
	#print "h=",h
	A = matrix(np.ones((1,dim)))
	b = matrix(1.0)
	sol = solvers.qp(P, q, -G, -h, A, b)
	return sol

def optimize_portfolio(stock_symbols, investment, exp_ret, startyear, endyear):
	
	if cached and os.path.isdir("./cache") == False:
		os.mkdir("./cache")
	
	price_mat = []
	avg_ret = []
	for stock in stock_symbols:
		print "Name of stock =" +stock
		ret = returns(stock, startyear, endyear) 
		avg_ret.append(np.mean(ret))	
		price_mat.append(np.array(ret))	
        #print "avg_ret=",avg_ret
	price_mat = np.array(price_mat)
	cov_mat = matrix(np.array(np.cov(price_mat)))
	avg_ret = np.transpose(matrix(avg_ret, (1,len(avg_ret)))) # make it a column vector
	sol = markwtz_opt(avg_ret, len(avg_ret),cov_mat,exp_ret)
	allocation = []
	if sol['status'] == 'optimal':
		#print 'Optimal solution found'
		print sol['x']
		allocation = [round(t,2) for t in sol['x'] * investment]
		print stock_symbols
		print allocation
		
	else:
		print 'Optimal solution not found'
	#print cov_mat
	#get avg return
	#get covariance matrix
	#do quadratic programming
	return allocation

if __name__ == "__main__":
	
	#Test code
	investment = 10000
	stock_symbols = ['IBM','GOOG','MSFT','T','AAPL','AMZN','YHOO','WMT','TSLA','INTC']
	expected_return = 5
	optimize_portfolio(stock_symbols, investment, expected_return)

