-- Useful SQLite queries for manual review.
SELECT COUNT(*) AS transaction_count, ROUND(SUM(net_sales), 2) AS net_sales
FROM transactions;

SELECT branch, COUNT(*) AS transactions, ROUND(SUM(net_sales), 2) AS net_sales
FROM transactions
GROUP BY branch
ORDER BY net_sales DESC;

SELECT product_name, SUM(quantity) AS units_sold, ROUND(SUM(net_sales), 2) AS net_sales
FROM transactions
GROUP BY product_id, product_name
ORDER BY net_sales DESC
LIMIT 10;

SELECT substr(transaction_date, 1, 7) AS year_month,
       ROUND(SUM(net_sales), 2) AS net_sales
FROM transactions
GROUP BY year_month
ORDER BY year_month;

SELECT anomaly_type, COUNT(*) AS finding_count
FROM anomalies
GROUP BY anomaly_type
ORDER BY finding_count DESC;
