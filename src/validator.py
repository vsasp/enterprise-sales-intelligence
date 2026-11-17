import pandas as pd

REQUIRED_COLUMNS = [
    "Transaction_ID", "Transaction_Date", "Customer_ID", "Customer_Name",
    "Product_ID", "Product_Name", "Category", "Branch", "Quantity",
    "Unit_Price", "Discount", "Payment_Method", "Order_Status"
]
NUMERIC_COLUMNS = ["Quantity", "Unit_Price", "Discount"]

def validate_schema(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "CSV is missing required columns: " + ", ".join(missing) +
            ". See README.md for the expected CSV format."
        )

def split_valid_invalid(df):
    """Return (valid rows, invalid rows with Validation_Issue column)."""
    validate_schema(df)
    work = df.copy()
    issues = pd.Series("", index=work.index, dtype="object")

    for col in ["Transaction_ID", "Customer_ID", "Product_ID", "Branch"]:
        bad = work[col].isna() | work[col].astype(str).str.strip().eq("")
        issues.loc[bad & issues.eq("")] = f"Missing {col}"

    dates = pd.to_datetime(work["Transaction_Date"], errors="coerce", dayfirst=False)
    bad_dates = dates.isna()
    issues.loc[bad_dates & issues.eq("")] = "Invalid Transaction_Date"

    for col in NUMERIC_COLUMNS:
        values = pd.to_numeric(work[col], errors="coerce")
        bad = values.isna()
        issues.loc[bad & issues.eq("")] = f"Invalid numeric value in {col}"

    quantity = pd.to_numeric(work["Quantity"], errors="coerce")
    price = pd.to_numeric(work["Unit_Price"], errors="coerce")
    discount = pd.to_numeric(work["Discount"], errors="coerce")
    bad_qty = quantity.notna() & (quantity <= 0)
    issues.loc[bad_qty & issues.eq("")] = "Quantity must be greater than zero"
    bad_price = price.notna() & (price < 0)
    issues.loc[bad_price & issues.eq("")] = "Unit_Price cannot be negative"
    bad_discount = discount.notna() & ((discount < 0) | (discount > 1))
    issues.loc[bad_discount & issues.eq("")] = "Discount must be between 0 and 1 (e.g. 0.10 for 10%)"

    invalid_mask = issues.ne("")
    invalid = work.loc[invalid_mask].copy()
    invalid["Validation_Issue"] = issues.loc[invalid_mask]
    valid = work.loc[~invalid_mask].copy()
    return valid, invalid
