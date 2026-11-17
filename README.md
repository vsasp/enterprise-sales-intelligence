# Enterprise Sales Data Processing, Analytics & Business Intelligence Automation System

A Python console-based project for Week 2: import multiple CSV sales files, validate and clean data, calculate sales metrics, analyze customers/products/branches/payments, flag rule-based anomalies, save records to SQLite, and generate CSV reports, a text management report, and PNG charts.

## Technology stack

- Python 3.x
- Pandas and NumPy (NumPy is available for additional numerical analysis)
- Matplotlib and Seaborn
- SQLite (`sqlite3`, built into Python)
- `os`/`pathlib`, `datetime`, and `logging`
- Jupyter Notebook / VS Code
- Git and GitHub

## Setup on Ubuntu

```bash
cd ~/Downloads
# If you extracted this folder elsewhere, cd into that folder instead.
cd enterprise-sales-intelligence

python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

The first run can process `data/raw/sample_sales.csv`. It creates the database automatically and writes reports/charts to the output folders.

## Input CSV format

CSV files go in `data/raw/`. All CSV files in that folder are combined. Column names must match these names (spaces are normalized to underscores):

`Transaction_ID, Transaction_Date, Customer_ID, Customer_Name, Product_ID, Product_Name, Category, Branch, Quantity, Unit_Price, Discount, Payment_Method, Order_Status`

`Discount` can be a fraction (`0.10`) or a percentage (`10`); values above 1 are treated as percentages. Dates should use ISO format such as `2026-01-15`. Quantity must be greater than zero and Unit_Price cannot be negative. Discounts must be between 0 and 1 after normalization.

Example:
```csv
Transaction_ID,Transaction_Date,Customer_ID,Customer_Name,Product_ID,Product_Name,Category,Branch,Quantity,Unit_Price,Discount,Payment_Method,Order_Status
TXN1001,2026-01-15,C001,Aarav Patil,P101,Wireless Mouse,Accessories,Pune,2,650,0.10,UPI,Completed
```

## Outputs

- `data/processed/cleaned_sales.csv`: cleaned and transformed records.
- `data/rejected/rejected_records.csv`: rows that fail validation, with a reason.
- `data/enterprise_sales.db`: SQLite database with transactions, quality logs, and anomaly logs.
- `reports/`: sales/customer/product/category/branch/payment/anomaly CSV files and a management text report.
- `visualizations/`: monthly sales line chart, branch bar chart, category pie chart, and top-products bar chart.
- `logs/application.log`: execution and error logs.

## Analysis included

- Total transactions, units sold, gross sales, discount amount, net sales, average transaction value.
- Monthly sales trend, payment method performance, repeat customer counts.
- Product, category, customer, and branch rankings.
- Rule-based anomaly flags for high discounts, unusually large quantities, and negative net sales.
- SQLite storage with transaction IDs as primary keys; duplicate transaction IDs are skipped when saved again.

## Important notes

- This is a rule-based analytics project, not a machine-learning fraud detector. Anomaly flags are prompts for human review, not proof of fraud.
- The SQLite database persists between runs. The same transaction ID will not be inserted twice. CSV reports are timestamped each run.
- Do not put the virtual environment, database, or sensitive customer data into a public GitHub repository.
- `notebooks/exploratory_analysis.ipynb` is a placeholder file created for the project structure. Open Jupyter and create notebook cells for any additional exploratory work.
