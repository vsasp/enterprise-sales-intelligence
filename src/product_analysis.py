import pandas as pd

def product_analysis(df):
    cols = ["Product_ID", "Product_Name", "Category", "Units_Sold", "Transactions", "Net_Sales"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    out = df.groupby(["Product_ID", "Product_Name", "Category"], dropna=False).agg(
        Units_Sold=("Quantity", "sum"),
        Transactions=("Transaction_ID", "nunique"),
        Net_Sales=("Net_Sales", "sum")
    ).reset_index()
    return out.sort_values("Net_Sales", ascending=False)

def category_analysis(df):
    if df.empty:
        return pd.DataFrame(columns=["Category", "Units_Sold", "Net_Sales"])
    return df.groupby("Category", dropna=False).agg(
        Units_Sold=("Quantity", "sum"), Net_Sales=("Net_Sales", "sum")
    ).reset_index().sort_values("Net_Sales", ascending=False)
