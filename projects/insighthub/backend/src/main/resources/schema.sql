CREATE TABLE IF NOT EXISTS sales_records (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id VARCHAR(20), order_date DATE,
  region VARCHAR(40), country VARCHAR(40), category VARCHAR(40),
  product VARCHAR(60), channel VARCHAR(30),
  units INT, revenue DOUBLE, profit DOUBLE, customer_id BIGINT
);
CREATE TABLE IF NOT EXISTS customers (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(60), segment VARCHAR(30), churn_risk DOUBLE
);
CREATE TABLE IF NOT EXISTS products (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(60), category VARCHAR(40), price DOUBLE
);
