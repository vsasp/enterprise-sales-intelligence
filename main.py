from pathlib import Path
import json
import logging
import sys
import pandas as pd

from src.data_loader import load_csv_files
from src.validator import split_valid_invalid
from src.cleaner import clean_data
from src.transformer import transform_data
from src.sales_analysis import sales_summary, monthly_sales, payment_analysis
from src.customer_analysis import customer_analysis, repeat_customer_summary
from src.product_analysis import product_analysis, category_analysis
from src.branch_analysis import branch_analysis
from src.anomaly_detector import detect_anomalies
from src.database import create_tables, save_sales_data, save_quality_issues, save_anomalies, get_database_summary
from src.report_generator import generate_outputs

BASE_DIR = Path(__file__).resolve().parent

def setup_logging():
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "application.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )

def read_config():
    path = BASE_DIR / "config" / "config.json"
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    setup_logging()
    logger = logging.getLogger("main")
    config = read_config()
    path = lambda key: BASE_DIR / config[key]

    for key in ["input_directory", "processed_directory", "rejected_directory",
                "reports_directory", "visualizations_directory"]:
        path(key).mkdir(parents=True, exist_ok=True)

    create_tables()
    raw = load_csv_files(path("input_directory"))
    if raw.empty:
        print("\nNo CSV files found in data/raw.")
        print("Add one or more sales CSV files there, then run: python main.py")
        print("A sample file is included at data/raw/sample_sales.csv")
        return

    print("\n[1/7] Validating source data...")
    try:
        valid, invalid = split_valid_invalid(raw)
    except ValueError as exc:
        logger.error("%s", exc)
        print(f"\nDATA FORMAT ERROR: {exc}")
        return

    if not invalid.empty:
        invalid.to_csv(path("rejected_directory") / "rejected_records.csv", index=False)
        logged = save_quality_issues(invalid)
        logger.warning("Rejected %s invalid rows; quality issues logged: %s", len(invalid), logged)
    print(f"Source rows: {len(raw)} | Valid: {len(valid)} | Rejected: {len(invalid)}")

    print("[2/7] Cleaning and deduplicating...")
    cleaned = clean_data(valid, config.get("duplicate_policy", "keep_first"))
    if cleaned.empty:
        print("No valid records remain after validation. Check data/rejected/rejected_records.csv.")
        return

    print("[3/7] Calculating sales metrics and calendar fields...")
    transformed = transform_data(cleaned)
    transformed.to_csv(path("processed_directory") / "cleaned_sales.csv", index=False)

    print("[4/7] Running sales, customer, product, branch and payment analysis...")
    summary = sales_summary(transformed)
    monthly = monthly_sales(transformed)
    customers = customer_analysis(transformed)
    products = product_analysis(transformed)
    categories = category_analysis(transformed)
    branches = branch_analysis(transformed)
    payments = payment_analysis(transformed)
    repeat = repeat_customer_summary(transformed)

    print("[5/7] Detecting rule-based anomalies...")
    anomalies = detect_anomalies(
        transformed,
        discount_threshold=float(config.get("anomaly_discount_threshold", 0.50)),
        high_quantity_threshold=float(config.get("high_quantity_threshold", 1000))
    )

    print("[6/7] Saving data and analysis records to SQLite...")
    db_result = save_sales_data(transformed)
    anomaly_count = save_anomalies(anomalies)

    print("[7/7] Generating management report and visualizations...")
    report = generate_outputs(
        transformed, summary, monthly, customers, products, categories, branches,
        payments, anomalies, path("reports_directory"), path("visualizations_directory"),
        top_n=int(config.get("top_n", 10))
    )

    print("\n" + "=" * 58)
    print("ENTERPRISE SALES INTELLIGENCE — RUN SUMMARY")
    print("=" * 58)
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title():25}: {value:,.2f}" if isinstance(value, float)
              else f"{key.replace('_', ' ').title():25}: {value:,}")
    print(f"{'Unique customers':25}: {repeat['unique_customers']:,}")
    print(f"{'Repeat customers':25}: {repeat['repeat_customers']:,}")
    print(f"{'Rows inserted in SQLite':25}: {db_result['inserted']:,}")
    print(f"{'Duplicate IDs skipped':25}: {db_result['skipped']:,}")
    print(f"{'Anomalies found this run':25}: {len(anomalies):,}")
    print(f"{'Anomalies logged in SQLite':25}: {anomaly_count:,}")
    print(f"\nManagement report: {report.relative_to(BASE_DIR)}")
    print(f"Processed data: data/processed/cleaned_sales.csv")
    print(f"Charts folder: {config['visualizations_directory']}/")
    print(f"Rejected rows: {config['rejected_directory']}/rejected_records.csv (if any)")
    print(f"Database: {Path(config['database_path'])}")
    print("\nDatabase status:", get_database_summary())
    print("\nFinished successfully.")

if __name__ == "__main__":
    main()
