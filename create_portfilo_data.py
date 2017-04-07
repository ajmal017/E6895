import sqlite3

excludelist = ['TRHC','TRVG','XPER','XCRA','WSFS','WPPGY','VRTS','VIVO','URBN','ZBRA','UHAL','UEIC','TZOO', 'TA']

def get_low_pe_stocks(n):
	with open('data/PE_ratio.txt','r') as pe:
		pe_data = {}
		company = {}
		lines = pe.read().split('\n')
		for line in lines:
			if line.strip() == "":
				continue
			x = line.split(':')
			if x[2] != None and x[0] not in excludelist and float(x[2]) >0:
				pe_data[x[0]] = float(x[2])
				company[x[0]] = x[1]
				#if x[0] in ["GE","IBM", "GOOG", "FB", "AAPL"]:
				#	print x[0]," ",x[1]
		stock_pe = sorted(pe_data.items(),key=lambda x:x[1])[0:n]
		return map(lambda x:(x[0],company[x[0]]), stock_pe)

def get_low_peg_stocks(n): # PE Growth ratio > 1
	with open('data/PE_growth_ratio.txt','r') as pe_growth:
		pe_growth_data = {}
		company = {}
		lines = pe_growth.read().split('\n')
		for line in lines:
			if line.strip() == "":
				continue
			x = line.split(':')
			if x[2] != None and x[0] not in excludelist and float(x[2]) > 2: #PE growth ration > 1
				pe_growth_data[x[0]] = float(x[2])
				company[x[0]] = x[1]
				#if x[0] in ["IBM", "GOOG", "FB", "AAPL"]:
				#	print x[0]," ",x[1]
		stock_peg = sorted(pe_growth_data.items(),key=lambda x:x[1])[0:n]
		return map(lambda x:(x[0],company[x[0]]), stock_peg)

def populate_data(symbols_company):

	conn = sqlite3.connect('data/portfolio.db')

	c = conn.cursor()

	with open('db_schema.sql','r') as f:
		sql = f.read()
		c.executescript(sql)

	categories = [(1, 'Technology'), (2,'Energy'), (3, 'Healthcare'), (4, 'Retailer')]
	c.executemany('INSERT INTO stock_categories VALUES (?,?)', categories)

	stocks = []
	for i in range(len(symbols_company)):
		stocks.append((i, symbols_company[i][0], symbols_company[i][1],'',1))

	#stocks = [(1,'IBM'),(1,'GOOG'),(1,'MSFT'),(1,'T'),(1,'AAPL'),(1,'AMZN'),(1,'YHOO'),(1,'TSLA'),(1,'INTC'), (4,'WMT')]
	c.executemany('INSERT INTO system_stocks VALUES (?,?,?,?,?)', stocks)

	for r in c.execute('SELECT * FROM stock_categories'):
		print r

	for r in c.execute('SELECT * FROM system_stocks'):
		print r	
	

	conn.commit()

	conn.close()


if __name__ == "__main__":
	stock_peg = get_low_peg_stocks(20)
	print stock_peg
	populate_data(stock_peg)
