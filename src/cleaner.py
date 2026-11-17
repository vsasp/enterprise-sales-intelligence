import pandas as pd

def clean_data(df, duplicate_policy="keep_first"):
    if df.empty:
        return df.copy()
    result = df.copy()
    result.columns = [str(c).strip().replace(" ", "_") for c in result.columns]

    text_cols = result.select_dtypes(include=["object", "string"]).columns
    for col in text_cols:
        result[col] = result[col].map(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    result["Transaction_Date"] = pd.to_datetime(
        result["Transaction_Date"], errors="coerce"
    )
    for col in ["Quantity", "Unit_Price", "Discount"]:
        result[col] = pd.to_numeric(result[col], errors="coerce")

    # Accept discounts entered as percentages such as 10, but normalize to 0.10.
    percent_mask = result["Discount"] > 1
    result.loc[percent_mask, "Discount"] = result.loc[percent_mask, "Discount"] / 100

    result["Discount"] = result["Discount"].clip(lower=0, upper=1)
    result["Customer_Name"] = result["Customer_Name"].fillna("Unknown Customer")
    result["Product_Name"] = result["Product_Name"].fillna("Unknown Product")
    result["Category"] = result["Category"].fillna("Uncategorized")
    result["Payment_Method"] = result["Payment_Method"].fillna("Unknown")
    result["Order_Status"] = result["Order_Status"].fillna("Unknown")

    if "Source_File" not in result.columns:
        result["Source_File"] = "unknown.csv"

    if duplicate_policy == "keep_first":
        result = result.drop_duplicates(subset=["Transaction_ID"], keep="first")
    elif duplicate_policy == "keep_last":
        result = result.drop_duplicates(subset=["Transaction_ID"], keep="last")
    elif duplicate_policy == "keep_all":
        pass
    else:
        raise ValueError("duplicate_policy must be keep_first, keep_last, or keep_all")
    return result.reset_index(drop=True)
