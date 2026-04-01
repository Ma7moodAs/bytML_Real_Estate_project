import pandas as pd
import numpy as np
import re


ARABIC_DIGIT_TRANSLATION = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def normalize_text(text):
    if pd.isna(text):
        return None
    normalized = str(text).translate(ARABIC_DIGIT_TRANSLATION)
    return re.sub(r"\s+", " ", normalized).strip()


def extract_number_from_patterns(text, patterns):
    normalized_text = normalize_text(text)
    if normalized_text is None:
        return None

    for pattern in patterns:
        match = re.search(pattern, normalized_text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1).replace(",", ""))
    return None


def extract_bathrooms_num(text):
    patterns = [
        r"(?:عدد\s*)?حمامات?\s*[:\-]?\s*(\d+)",
        r"(\d+)\s*حمامات?",
        r"(\d+)\s*حمام",
    ]
    return extract_number_from_patterns(text, patterns)


def extract_annualy_price(text):
    patterns = [
        r"(?:الايجار|الإيجار|السعر|القيمة)[^\n\r]{0,40}?(?:سنوي|سنويا|سنويًا)[^\d]{0,10}([\d,]+)",
        r"(?:سنوي|سنويا|سنويًا)[^\d]{0,10}([\d,]+)",
        r"([\d,]+)\s*(?:دينار|د\.?\s*ا)[^\n\r]{0,20}?(?:سنوي|سنويا|سنويًا)",
    ]
    return extract_number_from_patterns(text, patterns)


def extract_sale_price(text):
    patterns = [
        r"(?:سعر\s*البيع|السعر|الثمن|السعر\s*البيعي)[^\d]{0,10}([\d,]+)",
        r"(?:للبيع|بيع)[^\n\r]{0,30}?([\d,]+)\s*(?:دينار|د\.?\s*ا)",
        r"([\d,]+)\s*(?:دينار|د\.?\s*ا)[^\n\r]{0,20}?(?:للبيع|بيع)",
    ]
    return extract_number_from_patterns(text, patterns)


def fill_bathrooms_num(row):
    if pd.notna(row["Bathrooms"]):
        return row["Bathrooms"]

    value = extract_bathrooms_num(row["Description"])
    if value is None:
        value = extract_bathrooms_num(row["Specialities"])
    return value


def fill_annually_price(row):
    if pd.notna(row["Price_annualy"]):
        return row["Price_annualy"]

    value = extract_annualy_price(row["Specialities"])
    if pd.isna(value):
        value = extract_annualy_price(row["Description"])
    return value


def fill_sale_price(row):
    if pd.notna(row["Sale_price"]):
        return row["Sale_price"]

    value = extract_sale_price(row["Description"])
    if pd.isna(value):
        value = extract_sale_price(row["Specialities"])
    return value


def fill_bathrooms_from_text(df):
    result = df.copy()
    bathroom_mask = result["Bathrooms"].isna()
    result.loc[bathroom_mask, "Bathrooms"] = result.loc[bathroom_mask].apply(
        fill_bathrooms_num,
        axis=1,
    )
    return result


def fill_annual_price_from_text(df):
    result = df.copy()
    rent_mask = (result["Listing_type"] == "rent") & (result["Price_annualy"].isna())
    result.loc[rent_mask, "Price_annualy"] = result.loc[rent_mask].apply(
        fill_annually_price,
        axis=1,
    )
    return result


def fill_sale_price_from_text(df):
    result = df.copy()
    sale_mask = (result["Listing_type"] == "sale") & (result["Sale_price"].isna())
    result.loc[sale_mask, "Sale_price"] = result.loc[sale_mask].apply(
        fill_sale_price,
        axis=1,
    )
    return result


def run_feature_extraction_pass(df):
    result = df.copy()
    result = fill_bathrooms_from_text(result)
    result = fill_annual_price_from_text(result)
    result = fill_sale_price_from_text(result)
    return result


def cleaning_report(before_df, after_df):
    tracked_columns = ["Bathrooms", "Price_annualy", "Sale_price"]
    report = {}

    for column in tracked_columns:
        before_missing = int(before_df[column].isna().sum())
        after_missing = int(after_df[column].isna().sum())
        report[column] = {
            "missing_before": before_missing,
            "missing_after": after_missing,
            "filled": before_missing - after_missing,
        }

    return report


def clean_data(df):
    extracted_df = run_feature_extraction_pass(df)
    report = cleaning_report(df, extracted_df)
    return extracted_df, report



'''
def impute_price_from_similar_properties(df,target_col,listing_type,min_group_size=3):
    # use comparable properties from the same listing type and estimate price via median price per sqm
    type_mask = df['Listing_type'] == listing_type
    price_per_sqm = f'{target_col}_per_sqm'

    comparable_mask = type_mask & df[target_col].notna() & df['Area_sqm'].gt(0)
    df.loc[comparable_mask,price_per_sqm] = df.loc[comparable_mask,target_col] / df.loc[comparable_mask,'Area_sqm']

    missing_mask = type_mask & df[target_col].isna() & df['Area_sqm'].notna() & df['Area_sqm'].gt(0)

    for idx,row in df.loc[missing_mask,:].iterrows():
        group_candidates = [
            comparable_mask & (df['Location'] == row['Location']) & (df['Bedrooms'] == row['Bedrooms']),
            comparable_mask & (df['Location'] == row['Location']),
            comparable_mask & (df['Bedrooms'] == row['Bedrooms']),
            comparable_mask
        ]

        estimated_price = np.nan
        for candidate_mask in group_candidates:
            comparable_prices = df.loc[candidate_mask,price_per_sqm].dropna()
            if len(comparable_prices) >= min_group_size:
                estimated_price = comparable_prices.median() * row['Area_sqm']
                break

        if pd.notna(estimated_price):
            df.loc[idx,target_col] = round(estimated_price,2)

    df.drop(columns=[price_per_sqm],inplace=True,errors='ignore')
    return df

'''


'''

IMPORTANT_BINARY_FEATURES = {
    "has_parking": r"\bكراج\b",
    "has_elevator": r"\bمصعد\b",
    "has_storage": r"\bمخزن\b",
    "has_balcony": r"بلكون(?:ه|ات)?",
    "has_terrace": r"\bترس\b",
    "has_maid_room": r"غرفه\s*خادمه|\bخادمه\b",
    "has_laundry_room": r"غرفه\s*غسيل|\bغسيل\b",
    "has_central_ac": r"تكييف\s*مركزي",
    "has_ac_units": r"وحدات\s*تكييف|تكييف\s*وحدات",
    "has_heating": r"تدفيه|تدفئه|تدفئ",
    "has_built_in_kitchen": r"مطبخ\s*راكب",
    "has_wardrobes": r"خزاين(?:\s*بالحايط)?|خزائن(?:\s*بالحائط)?",
    "has_double_glazing": r"زجاج\s*دبل",
    "has_security_doors": r"ابواب\s*امان",
    "has_cctv": r"كاميرات\s*مراقبه",
    "has_hidden_lighting": r"اناره\s*مخفيه|سبوت\s*لايت|اناره\s*led",
    "has_deluxe_finish": r"تشطيبات\s*(?:سوبر\s*)?ديلوكس|تشطيبات\s*سوبرديلوكس",
}


def normalize_listing_text(text):
    if pd.isna(text):
        return ""

    text = str(text)
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ة": "ه",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
        "ـ": " ",
        "ndash;": "-",
        "–": "-",
        "—": "-",
        "+": " ",
        "*": " ",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    text = re.sub(r"[^\w\s\-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_text_column(df, description_col="Description", specialities_col="Specialities"):
    description = df.get(description_col, pd.Series("", index=df.index)).fillna("")
    specialities = df.get(specialities_col, pd.Series("", index=df.index)).fillna("")

    text = (description.astype(str) + " " + specialities.astype(str)).str.strip()
    return text.apply(normalize_listing_text)


def add_binary_features(df):
    df = df.copy()
    df["text"] = build_text_column(df)

    for column_name, pattern in IMPORTANT_BINARY_FEATURES.items():
        df[column_name] = df["text"].str.contains(pattern, regex=True, na=False).astype("int64")

    return df'''
