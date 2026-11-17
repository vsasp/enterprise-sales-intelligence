import pandas as pd

def branch_analysis(df):
    if df.empty:
        return pd.DataFrame(columns=["Branch", "Transactions", "Units_Sold", "Gross_Sales", "Net_Sales"])
    return df.groupby("Branch", dropna=False).agg(
        Transactions=("Transaction_ID", "nunique"),
        Units_Sold=("Quantity", "sum"),
        Gross_Sales=("Gross_Sales", "sum"),
        Net_Sales=("Net_Sales", "sum")
    ).reset_index().sort_values("Net_Sales", ascending=False)
