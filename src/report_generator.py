from pathlib import Path
from datetime import datetime
import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

LOGGER = logging.getLogger(__name__)

def _save_csv(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

def generate_outputs(df, summary, monthly, customers, products, categories, branches,
                     payments, anomalies, reports_dir, charts_dir, top_n=10):
    reports_dir, charts_dir = Path(reports_dir), Path(charts_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    datasets = {
        "monthly_sales": monthly,
        "customer_analysis": customers,
        "product_analysis": products,
        "category_analysis": categories,
        "branch_analysis": branches,
        "payment_analysis": payments,
        "anomalies": anomalies
    }
    for name, table in datasets.items():
        _save_csv(table, reports_dir / f"{name}_{stamp}.csv")

    if not df.empty:
        sns.set_theme(style="whitegrid")
        if not monthly.empty:
            plt.figure(figsize=(10, 5))
            sns.lineplot(data=monthly, x="Year_Month", y="Net_Sales", marker="o")
            plt.title("Monthly Net Sales Trend")
            plt.xlabel("Month")
            plt.ylabel("Net sales")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(charts_dir / f"monthly_sales_{stamp}.png", dpi=150)
            plt.close()

        if not branches.empty:
            plt.figure(figsize=(9, 5))
            plt.bar(branches["Branch"].astype(str), branches["Net_Sales"].astype(float))
            plt.title("Net Sales by Branch")
            plt.xlabel("Branch")
            plt.ylabel("Net sales")
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout()
            plt.savefig(charts_dir / f"branch_sales_{stamp}.png", dpi=150)
            plt.close()

        if not categories.empty:
            plot_data = categories.head(top_n)
            plt.figure(figsize=(8, 6))
            plt.pie(plot_data["Net_Sales"], labels=plot_data["Category"],
                    autopct="%1.1f%%", startangle=90)
            plt.title("Net Sales Share by Category")
            plt.tight_layout()
            plt.savefig(charts_dir / f"category_share_{stamp}.png", dpi=150)
            plt.close()

        if not products.empty:
            plot_data = products.head(top_n).sort_values("Net_Sales")
            plt.figure(figsize=(10, 6))
            plt.barh(plot_data["Product_Name"].astype(str), plot_data["Net_Sales"].astype(float))
            plt.title(f"Top {min(top_n, len(plot_data))} Products by Net Sales")
            plt.tight_layout()
            plt.savefig(charts_dir / f"top_products_{stamp}.png", dpi=150)
            plt.close()

    report_path = reports_dir / f"management_report_{stamp}.txt"
    lines = [
        "ENTERPRISE SALES INTELLIGENCE — MANAGEMENT REPORT",
        "=" * 55,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "KEY PERFORMANCE INDICATORS",
        "-" * 25
    ]
    for key, value in summary.items():
        lines.append(f"{key.replace('_', ' ').title()}: {value:,.2f}" if isinstance(value, float)
                     else f"{key.replace('_', ' ').title()}: {value:,}")
    lines += ["", "TOP BRANCHES BY NET SALES", "-" * 25]
    if branches.empty:
        lines.append("No branch data available.")
    else:
        for _, row in branches.head(top_n).iterrows():
            lines.append(f"{row['Branch']}: {row['Net_Sales']:,.2f}")
    lines += ["", "TOP PRODUCTS BY NET SALES", "-" * 25]
    if products.empty:
        lines.append("No product data available.")
    else:
        for _, row in products.head(top_n).iterrows():
            lines.append(f"{row['Product_Name']} ({row['Product_ID']}): {row['Net_Sales']:,.2f}")
    lines += ["", f"Detected anomaly records: {len(anomalies)}",
              "Note: anomalies are rule-based flags and should be reviewed, not treated as proof of fraud."]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    LOGGER.info("Reports written to %s", reports_dir)
    LOGGER.info("Charts written to %s", charts_dir)
    return report_path
