import pandas as pd

def customer_analysis(df):
    cols = ["Customer_ID", "Customer_Name", "Transactions", "Units", "Net_Sales"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    out = df.groupby(["Customer_ID", "Customer_Name"], dropna=False).agg(
        Transactions=("Transaction_ID", "nunique"),
        Units=("Quantity", "sum"),
        Net_Sales=("Net_Sales", "sum")
    ).reset_index()
    return out.sort_values("Net_Sales", ascending=False)

def repeat_customer_summary(df):
    if df.empty:
        return {"unique_customers": 0, "repeat_customers": 0}
    counts = df.groupby("Customer_ID")["Transaction_ID"].nunique()
    return {
        "unique_customers": int(counts.size),
        "repeat_customers": int((counts > 1).sum())
    }
