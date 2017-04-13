import os
from flask import Flask, jsonify, request, render_template
import sqlite3
import portfolio

app = Flask(__name__)

port = os.getenv('PORT', '5000')
startyear = 2012
endyear = 2016
@app.route('/', methods=['POST', 'GET'])
def porfolio():
	

	res = {}

	if request.method == 'POST':
		
		if request.form["investment"].strip() == "" or request.form["expectedreturn"].strip() == "":
			res["error"] = "Specify all input values"
		else:
			symbols = []
			companies = []
			categories = []
			category_set = set()
			
			conn = sqlite3.connect('data/portfolio.db')
			c = conn.cursor() 

			for r in c.execute('''select cat_name, symbol, company_name from stock_categories A, system_stocks B where A.cat_id = B.cat_id'''):
				#print r[1]
				#res['symbol'].append(r[1]+" : "+r[2])	
				categories.append(r[0])
				category_set.add(r[0])
				symbols.append(r[1])
				companies.append(r[2])
			#print res['symbol']
			#if request.method == 'POST':	
			#res["allocation"] = portfolio.optimize_portfolio(res['symbol'], float(request.form['investment']), float(request.form['expectedreturn']), startyear, endyear)		
			#allocation = portfolio.optimize_portfolio_parallel(symbols, float(request.form['investment']), float(request.form['expectedreturn']), startyear, endyear)		
			allocation = portfolio.optimize_portfolio_by_categories(symbols, float(request.form['investment']), float(request.form['expectedreturn']), startyear, endyear)		
			res['portfolio'] = {}	
			for cs in category_set:
				res['portfolio'][cs] = {}
				res['portfolio'][cs]['symbol'] = []
				res['portfolio'][cs]['company'] = []
				res['portfolio'][cs]['allocation'] = []

			for i in range(len(allocation)):
				if allocation[i] > 0:
					res['portfolio'][categories[i]]["symbol"].append(symbols[i])
					res['portfolio'][categories[i]]["company"].append(companies[i])
					res['portfolio'][categories[i]]["allocation"].append(allocation[i])

			res["investment"] = request.form['investment']
			res['expectedreturn'] = request.form['expectedreturn']		
		
			conn.close()

	return render_template('optimize.html', result=res)

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=int(port))

