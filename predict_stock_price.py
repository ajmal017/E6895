import numpy as np
from sklearn import datasets, linear_model
import glob
import sqlite3


def predict_and_store_all_stock_returns(startyear, endyear, futureyears):
	conn = sqlite3.connect('data/portfolio.db')
	c = conn.cursor()

	c.execute('DELETE FROM predicted_returns')
	conn.commit()

	for fname in glob.glob('cache/*_'+str(startyear)+'_'+str(endyear)):
		stock_symbol = fname.split('/')[1].split('_')[0]
		#print "******", stock_symbol, "******"
		with open(fname, 'r') as f:
			price_history = []
			f.readline()
			for line in f:
				if line.strip() == "":
					continue
				price_history.insert(0,float(line.split(',')[5]))
			X = np.array(range(0,len(price_history)))[:,np.newaxis,]
			y = np.array(price_history)[:,np.newaxis]	
			
			#X_train = X[:-20]
			#X_test = X[-20:]
			#y_train = y[:-20]
			#y_test = y[-20:]
			
			regr = linear_model.LinearRegression()
			
			#regr.fit(X_train, y_train)
			# The coefficients
			#print('Coefficients: \n', regr.coef_)
			# The mean squared error
			#print("Mean squared error: %.2f" % np.mean((regr.predict(X_test) - y_test) ** 2))
			# Explained variance score: 1 is perfect prediction
			#print('Variance score: %.2f' % regr.score(X_test, y_test))
			regr.fit(X, y)

			predict_startyr = endyear + 1
			predicted_returns = []
			lastprice = X[-1:][0][0]
			for i in range(futureyears):
				p = regr.predict(len(X) - 1 + i*12)[0][0]
				print "Predicted value for year ", str(predict_startyr+i), " = ", p
				predicted_returns.append(p - lastprice)
				t = (stock_symbol,)
				c.execute('SELECT stock_id FROM system_stocks WHERE symbol=?', t)
				stock_id =  c.fetchone()
				if stock_id != None:
					t = (stock_id[0], predict_startyr + i, p - lastprice)	
					c.execute('insert into predicted_returns values(?,?,?)',t)
				lastprice = p
			print predicted_returns			

		conn.commit()

	conn.close()

def predict_and_store_returns(stock_symbol, startyear, endyear, futureyears):
	conn = sqlite3.connect('data/portfolio.db')
	c = conn.cursor()

	t = (stock_symbol,)
	c.execute('DELETE FROM predicted_returns where stock_id in (select stock_id from system_stocks where symbol=?)', t)
	conn.commit()

	print "******", stock_symbol, "******"
	with open('cache/'+stock_symbol+'_'+str(startyear)+'_'+str(endyear), 'r') as f:
		price_history = []
		f.readline()
		for line in f:
			if line.strip() == "":
				continue
			price_history.insert(0,float(line.split(',')[5]))
		X = np.array(range(0,len(price_history)))[:,np.newaxis,]
		y = np.array(price_history)[:,np.newaxis]			

		yr = 2012
		for p in range(11, len(price_history), 12):
			print "Historical value for year ",str(yr)," = ", price_history[p]
			yr += 1			
	
		regr = linear_model.LinearRegression()
		regr.fit(X, y)
		# The coefficients
		print('Coefficients: \n', regr.coef_)

		predict_startyr = endyear + 1
		predicted_returns = []
		lastprice = X[-1:][0][0]
		for i in range(futureyears):
			p = regr.predict(len(X) - 1 + i*12)[0][0]
			print "Predicted value for year ", str(predict_startyr+i), " = ", p
			predicted_returns.append(p - lastprice)
			t = (stock_symbol,)
			c.execute('SELECT stock_id FROM system_stocks WHERE symbol=?', t)
			stock_id =  c.fetchone()
			if stock_id != None:
				t = (stock_id[0], predict_startyr + i, p - lastprice)	
				c.execute('insert into predicted_returns values(?,?,?)',t)
			lastprice = p
		print predicted_returns		


		conn.commit()

#This function is not implmenented. Anyone 	
def obtain_and_store_future_returns(api_url, stock_symbol, startyear, endyear, futureyears):
	conn = sqlite3.connect('data/portfolio.db')
	c = conn.cursor()

	t = (stock_symbol,)
	c.execute('DELETE FROM predicted_returns where stock_id in (select stock_id from system_stocks where symbol=?)', t)
	conn.commit()

	print "******", stock_symbol, "******"

	price_history = []
	#***********************************************************
	# Implement here the API call for stock_symbol, and parsing of the returned data,
        # Populate price_history list with the predicted price (one closing price per year) for the futureyears
	#***********************************************************

	regr = linear_model.LinearRegression()
	regr.fit(X, y)
	# The coefficients
	print('Coefficients: \n', regr.coef_)

	predict_startyr = endyear + 1
	predicted_returns = []
	lastprice = X[-1:][0][0]
	for i in range(futureyears):
		p = regr.predict(len(X) - 1 + i*12)[0][0]
		print "Predicted value for year ", str(predict_startyr+i), " = ", p
		predicted_returns.append(p - lastprice)
		t = (stock_symbol,)
		c.execute('SELECT stock_id FROM system_stocks WHERE symbol=?', t)
		stock_id =  c.fetchone()
		if stock_id != None:
			t = (stock_id[0], predict_startyr + i, p - lastprice)	
			c.execute('insert into predicted_returns values(?,?,?)',t)
		lastprice = p
	print predicted_returns		


	conn.commit()	

if __name__ == "__main__":
	startyear=2012
	endyear=2016

	predict_and_store_all_stock_returns(startyear, endyear, 30)
	#predict_and_store_returns('AMZN', startyear, endyear, 30)
