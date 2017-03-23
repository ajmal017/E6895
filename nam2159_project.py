import os
from flask import Flask, jsonify, request, render_template
import sqlite3
import portfolio

app = Flask(__name__)

port = os.getenv('PORT', '5000')
startyear = 2014
endyear = 2016
@app.route('/', methods=['POST', 'GET'])
def porfolio():
	

	res = {}

	if request.method == 'POST':
		
		if request.form["investment"].strip() == "" or request.form["expectedreturn"].strip() == "":
			res["error"] = "Specify all input values"
		else:
			res['symbol'] = []
			res['company'] = []
			
			conn = sqlite3.connect('data/portfolio.db')
			c = conn.cursor() 

			for r in c.execute('''select cat_name, symbol, company from categories A, stocks B where A.category_id = B.category'''):
				print r[1]
				#res['symbol'].append(r[1]+" : "+r[2])	
				res['symbol'].append(r[1])
				res['company'].append(r[2])
			print res['symbol']
			#if request.method == 'POST':	
			res["allocation"] = portfolio.optimize_portfolio(res['symbol'], float(request.form['investment']), float(request.form['expectedreturn']), startyear, endyear)		
				
			conn.close()

	return render_template('optimize.html', result=res)



if __name__ == "__main__":
        app.run(host='0.0.0.0', port=int(port))

