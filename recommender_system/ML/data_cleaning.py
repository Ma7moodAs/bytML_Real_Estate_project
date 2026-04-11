import pandas as pd
import numpy as np
import re


def extract_data(text, patterns, return_type='float'):
    if pd.isna(text):
        return np.nan

    for pattern in patterns:
        match_pattern = re.search(pattern=pattern, string=str(text))
        if match_pattern:
            try:
                value = match_pattern.group(1).replace(",", "")
                if return_type == 'int':
                    return int(float(value))
                else:
                    return float(value)
            except:
                return np.nan
    return np.nan



def extract_bedrooms_num(text):
    patterns = [
        r"(\d+)\s*غرف\s*نوم",
        r"غرف\s*نوم\s*عدد\s*(\d+)",
        r"(\d+)\s*غرفة\s*نوم",
        r"غرفة\s*نوم\s*عدد\s*(\d+)",
    ]
    value = extract_data(text, patterns,return_type='int')
    if pd.notna(value):
        return value

    if pd.notna(text) and re.search(r"غرفة\s*نوم(?:\s*ماستر)?", str(text)):
        return 1

    if pd.notna(text) and re.search(r"غرف\s*نوم\s*ماستر", str(text)):
        return 1

    return np.nan


def extract_bathrooms_num(text):
    patterns = [
        r"(\d+)\s*حمامات",
        r"حمامات\s*عدد\s*(\d+)",
        r"(\d+)\s*حمام",
    ]
    return extract_data(text, patterns,return_type='int')


def extract_annualy_price(text):
    patterns = [
        r"السعر\s*\(?سنوي(?:ا|اً)?\)?\s*[:\-]?\s*([\d,]+)",
        r"سنوي(?:ا|اً)?\s*[:\-]?\s*([\d,]+)",
        r"([\d,]+)\s*دينار(?:\s*اردني)?\s*(?:سنوي|سنويا|سنوياً)",
        r"السعر\s*[:\-]?\s*([\d,]+)",
    ]
    return extract_data(text, patterns, return_type='float')


def extract_sale_price(text):
    patterns = [
        r"السعر\s*[:\-]?\s*([\d,]+)",
        r"سعر\s*\(?البيع\)?\s*[:\-]?\s*([\d,]+)",
    ]
    return extract_data(text, patterns,return_type='float')


def fill_bedrooms_num(row):
    if pd.notna(row["Bedrooms"]) and row["Bedrooms"] != 0:
        return row["Bedrooms"]

    value = extract_bedrooms_num(row["Description"])
    if pd.isna(value):
        value = extract_bedrooms_num(row["Specialities"])
    return value


def fill_bathrooms_num(row):
    if pd.notna(row["Bathrooms"]):
        return row["Bathrooms"]

    value = extract_bathrooms_num(row["Description"])
    if pd.isna(value):
        value = extract_bathrooms_num(row["Specialities"])
    return value


def fill_annualy_price(row):
    if (pd.notna(row["Price_annualy"])) and (row['Price_annualy'] > 1000):
        return row["Price_annualy"]

    value = extract_annualy_price(row["Specialities"])
    if pd.isna(value):
        value = extract_annualy_price(row["Description"])
    return value


def fill_sale_price(row):
    if (pd.notna(row["Sale_price"]) and row['Sale_price'] > 1000):
        return row["Sale_price"]

    value = extract_sale_price(row["Description"])
    if pd.isna(value):
        value = extract_sale_price(row["Specialities"])
    return value


def feature_recovery(df):
    bed_mask = df["Bedrooms"].isna() | (df["Bedrooms"] == 0)
    df.loc[bed_mask, "Bedrooms"] = df.loc[bed_mask, :].apply(fill_bedrooms_num, axis=1)

    bath_mask = df["Bathrooms"].isna()
    df.loc[bath_mask, "Bathrooms"] = df.loc[bath_mask, :].apply(fill_bathrooms_num, axis=1)
 
    annualy_price_mask = ((df["Price_annualy"].isna()) | (df['Price_annualy'] <= 1000))\
          & (df["Listing_type"] == "rent")
    df.loc[annualy_price_mask, "Price_annualy"] = df.loc[annualy_price_mask, :].apply(
        fill_annualy_price,
        axis=1,
    )

    sale_price_mask = ((df["Sale_price"].isna()) | (df['Sale_price'] <= 1000))\
          & (df["Listing_type"] == "sale")
    df.loc[sale_price_mask, "Sale_price"] = df.loc[sale_price_mask, :].apply(
        fill_sale_price,
        axis=1,
    )

    return df


def missing_values_handling(df):
    df["Bedrooms"] = df["Bedrooms"].fillna(df["Bedrooms"].median())
    df["Bathrooms"] = df.groupby("Bedrooms")["Bathrooms"].transform(lambda x: x.fillna(x.median()))
    df["Area_sqm"] = df["Area_sqm"].fillna(df["Area_sqm"].median())

    df[["Floor", "Floor_type"]] = df[["Floor", "Floor_type"]].fillna("Unknown")
    df["Description"] = df["Description"].fillna("")
    df["Specialities"] = df["Specialities"].fillna("")

    df = df.dropna(subset=["Location"]).copy()

    # Treat invalid sale-price outliers as missing so they are removed with the unresolved prices.
    #df.loc[(df["Listing_type"] == "sale") & (df["Sale_price"] == 1), "Sale_price"] = np.nan
    # comment out the above line because I have fixed the invalid prices 
    # by extracting them using the feature extraction functions, so there is no need 
    # for this line because it will be redundant 
    # and will cause the code to break if it tries to convert the valid prices that I have
    #  extracted to NaN
    
    df["Final_price"] = np.where(
        df["Listing_type"] == "sale",
        df["Sale_price"],
        df["Price_annualy"],
    )

    df = df.dropna(subset=["Final_price"])
    df = df.drop(columns=["Price_annualy", "Sale_price", "URL", "Price_monthly"], errors="ignore")

    return df


def fix_dtypes(df):
    df["Bedrooms"] = df["Bedrooms"].astype("Int64") # Int64 allows NaN values, unlike int46 which does not and causes the code to break when the data contains Nan
    df["Bathrooms"] = df["Bathrooms"].astype("Int64")
    df["Area_sqm"] = df["Area_sqm"].astype("float64")
    df["Final_price"] = df["Final_price"].astype("float64")
    return df


def clean_data(df):
    df = feature_recovery(df)
    df = missing_values_handling(df)
    df = fix_dtypes(df)
    return df
