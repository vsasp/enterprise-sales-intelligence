import pandas as pd

def transform_data(df):
    if df.empty:
        return df.copy()
    result = df.copy()
    result["Gross_Sales"] = result["Quantity"] * result["Unit_Price"]
    result["Discount_Amount"] = result["Gross_Sales"] * result["Discount"]
    result["Net_Sales"] = (result["Gross_Sales"] - result["Discount_Amount"]).round(2)
    result["Transaction_Date"] = pd.to_datetime(result["Transaction_Date"])
    result["Year"] = result["Transaction_Date"].dt.year
    result["Month"] = result["Transaction_Date"].dt.month
    result["Month_Name"] = result["Transaction_Date"].dt.strftime("%b")
    result["Year_Month"] = result["Transaction_Date"].dt.to_period("M").astype(str)
    return result
