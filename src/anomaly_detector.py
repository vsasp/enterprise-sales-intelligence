import pandas as pd

def detect_anomalies(df, discount_threshold=0.50, high_quantity_threshold=1000):
    columns = ["Transaction_ID", "Anomaly_Type", "Details", "Net_Sales"]
    if df.empty:
        return pd.DataFrame(columns=columns)
    findings = []
    for _, row in df.iterrows():
        tid = str(row.get("Transaction_ID", ""))
        net = row.get("Net_Sales", 0)
        discount = row.get("Discount", 0)
        qty = row.get("Quantity", 0)
        if pd.notna(discount) and float(discount) >= discount_threshold:
            findings.append({"Transaction_ID": tid, "Anomaly_Type": "High discount",
                             "Details": f"Discount is {float(discount):.0%}; review promotion/approval.",
                             "Net_Sales": net})
        if pd.notna(qty) and float(qty) >= high_quantity_threshold:
            findings.append({"Transaction_ID": tid, "Anomaly_Type": "Unusually high quantity",
                             "Details": f"Quantity is {qty}; confirm order and units.",
                             "Net_Sales": net})
        if pd.notna(net) and float(net) < 0:
            findings.append({"Transaction_ID": tid, "Anomaly_Type": "Negative net sales",
                             "Details": "Net sales is negative; review source data and business rules.",
                             "Net_Sales": net})
    return pd.DataFrame(findings, columns=columns)
