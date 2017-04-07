DROP TABLE IF EXISTS users;

CREATE TABLE users(
 cust_id INTEGER PRIMARY KEY,
 name TEXT,
 address TEXT,
 email TEXT
);

DROP TABLE IF EXISTS investment;

CREATE TABLE investment(
  cust_id INTEGER,
  invest_date TEXT,
  amount REAL,
  FOREIGN KEY(cust_id) REFERENCES users(cust_id)
);

DROP TABLE IF EXISTS stock_categories;

CREATE TABLE stock_categories(
  cat_id INTEGER PRIMARY KEY,
  cat_name TEXT
);


DROP TABLE IF EXISTS system_stocks;

CREATE TABLE system_stocks(
  stock_id INTEGER PRIMARY KEY,
  symbol TEXT,
  company_name TEXT,
  start_year TEXT,
  cat_id INTEGER,
  FOREIGN KEY(cat_id) REFERENCES stock_category(cat_id)
);

DROP TABLE IF EXISTS stock_returns;

CREATE TABLE stock_returns(
  stock_id INTEGER,
  year TEXT,
  avg_return REAL,
  FOREIGN KEY(stock_id) REFERENCES system_stocks(stock_id)
);


DROP TABLE IF EXISTS allocation;

create table allocation(
  cust_id INTEGER,
  stock_id INTEGER,
  amount REAL,
  FOREIGN KEY(cust_id) REFERENCES users(cust_id),
  FOREIGN KEY(stock_id) REFERENCES system_stocks(stock_id)
);
