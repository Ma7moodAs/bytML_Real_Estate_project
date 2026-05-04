"""Validation helpers for the recommender input dataset."""

import pandas as pd


REQUIRED_COLUMNS = [
    "Listing_type",
    "Bedrooms",
    "Bathrooms",
    "Area_sqm",
    "Furnished",
    "Pool",
    "Floor",
    "Floor_type",
    "Location",
    "Description",
    "Specialities",
]

ALLOWED_LISTING_TYPES = {"sale", "rent"}

NUMERIC_COLUMNS = [
    "Bedrooms",
    "Bathrooms",
    "Area_sqm",
    "Price_annualy",
    "Sale_price",
    "Price_monthly",
    "apartment_id",
]

BOOLEAN_COLUMNS = [
    "Furnished",
    "Pool",
]

IDENTIFIER_COLUMN = "apartment_id"


def check_required_columns(df, required_columns=None, require_identifier=False):
    required_columns = required_columns or REQUIRED_COLUMNS
    expected_columns = list(required_columns)

    missing_columns = [col for col in expected_columns if col not in df.columns]

    if missing_columns:
        return [f"Missing required columns: {missing_columns}"]

    return []


def check_listing_type_values(df):
    if "Listing_type" not in df.columns:
        return []

    invalid_values = (
        df["Listing_type"]
        .dropna()
        .loc[lambda values: ~values.isin(ALLOWED_LISTING_TYPES)]
        .unique()
        .tolist()
    )

    if invalid_values:
        return [f"Invalid Listing_type values found: {invalid_values}"]

    return []


def check_numeric_columns(df):
    errors = []

    for column in NUMERIC_COLUMNS:
        if column not in df.columns:
            continue

        converted = pd.to_numeric(df[column], errors="coerce")
        invalid_mask = df[column].notna() & converted.isna()

        if invalid_mask.any():
            errors.append(
                f"Column '{column}' contains non-numeric values in {int(invalid_mask.sum())} rows."
            )

    return errors


def check_boolean_columns(df):
    errors = []
    valid_boolean_values = {0, 1, True, False}

    for column in BOOLEAN_COLUMNS:
        if column not in df.columns:
            continue

        values = set(df[column].dropna().unique().tolist())

        if not values.issubset(valid_boolean_values):
            errors.append(
                f"Column '{column}' contains invalid boolean-like values: {sorted(values)}"
            )

    return errors


def check_price_rules(df):
    errors = []

    if "Listing_type" not in df.columns:
        return errors

    sale_mask = df["Listing_type"] == "sale"
    rent_mask = df["Listing_type"] == "rent"

    if sale_mask.any():
        if "Sale_price" not in df.columns:
            errors.append("Sale listings exist, but the 'Sale_price' column is missing.")
        else:
            sale_price = pd.to_numeric(df["Sale_price"], errors="coerce")
            missing_sale_price = sale_mask & sale_price.isna()

            if missing_sale_price.any():
                errors.append(
                    f"Sale listings with missing Sale_price: {int(missing_sale_price.sum())}"
                )

    if rent_mask.any():
        if "Price_annualy" not in df.columns:
            errors.append("Rent listings exist, but the 'Price_annualy' column is missing.")
            return errors

        annual_price = pd.to_numeric(df["Price_annualy"], errors="coerce")
        missing_rent_price = rent_mask & annual_price.isna()

        if missing_rent_price.any():
            errors.append(
                f"Rent listings with missing Price_annualy: {int(missing_rent_price.sum())}"
            )

    return errors


def check_identifier_column(df, identifier_col=IDENTIFIER_COLUMN, required=False):
    if identifier_col not in df.columns:
        if required:
            return [f"Missing required identifier column: '{identifier_col}'"]
        return []

    errors = []
    identifier_values = pd.to_numeric(df[identifier_col], errors="coerce")
    invalid_identifier_mask = df[identifier_col].notna() & identifier_values.isna()

    if invalid_identifier_mask.any():
        errors.append(
            f"Column '{identifier_col}' contains non-numeric values in {int(invalid_identifier_mask.sum())} rows."
        )

    if df[identifier_col].duplicated().any():
        errors.append(f"Column '{identifier_col}' contains duplicate values.")

    if df[identifier_col].isna().any():
        errors.append(f"Column '{identifier_col}' contains missing values.")

    return errors


def validate_property_data(df, require_identifier=False):
    errors = []

    errors.extend(check_required_columns(df, require_identifier=require_identifier))
    errors.extend(check_listing_type_values(df))
    errors.extend(check_numeric_columns(df))
    errors.extend(check_boolean_columns(df))
    errors.extend(check_price_rules(df))
    errors.extend(check_identifier_column(df, required=require_identifier))

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }

