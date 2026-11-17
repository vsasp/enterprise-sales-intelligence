import pandas as pd

def sales_summary(df):
    if df.empty:
        return {"transactions": 0, "units_sold": 0, "gross_sales": 0.0,
                "discount_amount": 0.0, "net_sales": 0.0, "average_order_value": 0.0}
    net = pd.to_numeric(df["Net_Sales"], errors="coerce").fillna(0)
    return {
        "transactions": int(df["Transaction_ID"].nunique()),
        "units_sold": int(df["Quantity"].sum()),
        "gross_sales": round(float(df["Gross_Sales"].sum()), 2),
        "discount_amount": round(float(df["Discount_Amount"].sum()), 2),
        "net_sales": round(float(net.sum()), 2),
        "average_order_value": round(float(net.mean()), 2)
    }

def monthly_sales(df):
    if df.empty:
        return pd.DataFrame(columns=["Year_Month", "Gross_Sales", "Discount_Amount", "Net_Sales"])
    return df.groupby("Year_Month", as_index=False)[
        ["Gross_Sales", "Discount_Amount", "Net_Sales"]
    ].sum().sort_values("Year_Month")

def payment_analysis(df):
    if df.empty:
        return pd.DataFrame(columns=["Payment_Method", "Transactions", "Net_Sales"])
    return df.groupby("Payment_Method", dropna=False).agg(
        Transactions=("Transaction_ID", "nunique"),
        Net_Sales=("Net_Sales", "sum")
    ).reset_index().sort_values("Net_Sales", ascending=False)
