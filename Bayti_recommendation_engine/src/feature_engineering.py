import re

import pandas as pd


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

    return df
