import sys
import time
import urllib2
import csv
import os
import numpy as np
import sqlite3
from collections import defaultdict
from yahoo_finance import Share
from cvxopt import matrix, solvers
from multiprocessing.pool import ThreadPool

cached = True
OPT_BUCKET_SIZE = 300

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
		#"""
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
			
		histdata = csv.DictReader(response)
		#"""
		#stock = Share(stocksymbol)
		#histdata = stock.get_historical(str(startyear)+'-01-01',str(endyear)+'-12-31') #Jan 1 of startyear through Dec 31 of endyear		

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
	conn = sqlite3.connect('data/portfolio.db')
	c = conn.cursor()
        t = (startyear, endyear, stocksymbol)
	c.execute('select B.year, B.yearly_return from system_stocks A, stock_returns B where A.stock_id = B.stock_id and B.year >=? and B.year<=? and A.symbol=?', t) 
	rows = c.fetchall()
	ret = [] 
	#print "NUMBER OF ROWS ",len(rows)	
	if len(rows) > 1:
		ret = map(lambda x:x[1], rows)
		#print "Reading from database"
	else:
		price_dict = get_price_history(stocksymbol, startyear, endyear)
		
		t = (stocksymbol,)
		c.execute('select stock_id from system_stocks where symbol=?',t)
		stock_id = c.fetchone()[0]
		#print stock_id, stocksymbol	
		
		prices = []
		years = []
		if len(price_dict["Open"]) > 0:
			prices.insert(0,float(price_dict["Open"][0]))
		for i in  range(0, len(price_dict["Date"])-1 ):
			yr = 	price_dict["Date"][i].split('-')[0]
			yrnext = price_dict["Date"][i+1].split('-')[0]
			if yr != yrnext:
				prices.append(float(price_dict["Close"][i]))
				years.append(int(yr))
			if i == len(price_dict["Date"]) - 2: #last entry
				prices.append(float(price_dict["Close"][i]))
				years.append(int(yrnext))
							
		
		#prices = [float(x) for x in price_dict["Close"]]
		#prices.insert(0,float(price_dict["Open"][0]))
		#prices = [ prices[i] for i in range(0,len(prices),12)]
		#years = map(lambda x:int(x.split('-')[0]), price_dict["Date"]) 
		#years = [ years[y] for y in range(0, len(years),12)]
		#print years
		ret = [(prices[i+1] - prices[i]) for i in range(len(prices)-1)]
		#print ret
		for y in range(len(years)):
			t = (stock_id, years[y], ret[y])	
			c.execute('insert into stock_returns values(?,?,?)',t)
		conn.commit()	
		#print prices

	# if the stock went public after the startyear, put 0.0 return for those years
	if len(ret) < (endyear - startyear + 1): 
		for i in range(endyear -startyear + 1 - len(ret) ):
			ret.insert(0, 0.0)
	#print ret
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
		#print "Name of stock =" +stock
		ret = returns(stock, startyear, endyear) 
		avg_ret.append(np.mean(ret))	
		price_mat.append(np.array(ret))	
        #print "avg_ret=",avg_ret, "len=", len(avg_ret)
        #print "price_mat=",price_mat, "len=", len(price_mat)
	price_mat = np.array(price_mat)
	cov_mat = matrix(np.array(np.cov(price_mat)))
	avg_ret = np.transpose(matrix(avg_ret, (1,len(avg_ret)))) # make it a column vector
	sol = markwtz_opt(avg_ret, len(avg_ret),cov_mat,exp_ret)
	allocation = []
	if sol['status'] == 'optimal':
		#print 'Optimal solution found'
		#print sol['x']
		allocation = [round(t,2) for t in sol['x'] * investment]
		#print stock_symbols
		#print allocation
		
	else:
		print 'Optimal solution not found'
	#print cov_mat
	#get avg return
	#get covariance matrix
	#do quadratic programming
	return allocation

def optimize_portfolio_parallel(stock_symbols, investment, exp_ret, startyear, endyear):
	
	if cached and os.path.isdir("./cache") == False:
		os.mkdir("./cache")
	num_buckets = len(stock_symbols) / OPT_BUCKET_SIZE
	if len(stock_symbols) % OPT_BUCKET_SIZE != 0:
		num_buckets += 1
	allocation = []
	alloc_table = {}

	pool = ThreadPool(num_buckets) #num_threaads
	for i in range(num_buckets):
		stocks_bucket = []
		invest_bucket = 0
		if i == num_buckets - 1:
			stocks_bucket = stock_symbols[i*OPT_BUCKET_SIZE:]
			invest_bucket = (len(stock_symbols) - i*OPT_BUCKET_SIZE)*1.0*investment/len(stock_symbols)
		else:
			stocks_bucket = stock_symbols[i*OPT_BUCKET_SIZE: (i+1)*OPT_BUCKET_SIZE]
			invest_bucket = OPT_BUCKET_SIZE*1.0*investment/len(stock_symbols)
		alloc_table[i] = pool.apply_async(optimize_portfolio, (stocks_bucket, invest_bucket, exp_ret, startyear, endyear)).get()
		#allocation.extend(optimize_portfolio(stocks_bucket, invest_bucket, exp_ret, startyear, endyear))		
		#allocation = pool.map(optimize_portfolio, (stocks_bucket, invest_bucket, exp_ret, startyear, endyear))
	pool.close()
	pool.join()

	for k in alloc_table.keys():
		allocation.extend(alloc_table[k])	
		print "Key =",k," allocation size = ",len(allocation)

	return allocation

def optimize_portfolio_by_categories(stock_symbols, investment, exp_ret, startyear, endyear):
	
	if cached and os.path.isdir("./cache") == False:
		os.mkdir("./cache")
		
	stocks_by_categories = {}
	conn = sqlite3.connect('data/portfolio.db')
	c = conn.cursor()
	for row in c.execute('select distinct symbol, cat_name from system_stocks A, stock_categories B where A.cat_id = B.cat_id'):
		if row[1] not in stocks_by_categories:
			stocks_by_categories[row[1]] = []
		stocks_by_categories[row[1]].append(row[0]) 
	
	conn.close()
	print stocks_by_categories	

	allocation = []
	alloc_table = {}

	num_threads = len(stocks_by_categories.keys())
	pool = ThreadPool(num_threads)
	for k in stocks_by_categories.keys():
		stocks_bucket = stocks_by_categories[k]
		invest_bucket = len(stocks_bucket)*1.0*investment/len(stock_symbols)
		alloc_table[k] = pool.apply_async(optimize_portfolio, (stocks_bucket, invest_bucket, exp_ret, startyear, endyear)).get()
		#allocation.extend(optimize_portfolio(stocks_bucket, invest_bucket, exp_ret, startyear, endyear))		
		#allocation = pool.map(optimize_portfolio, (stocks_bucket, invest_bucket, exp_ret, startyear, endyear))
	pool.close()
	pool.join()

	for k in alloc_table.keys():
		allocation.extend(alloc_table[k])	
		print "Key =",k," allocation size = ",len(allocation)

	return allocation

if __name__ == "__main__":
	
	#Test code
	investment = 10000
	stock_symbols = ['IBM','GOOG','MSFT','T','AAPL','AMZN','YHOO','WMT','TSLA','INTC']
	expected_return = 5
	optimize_portfolio(stock_symbols, investment, expected_return)

