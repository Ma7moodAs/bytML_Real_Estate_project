import pandas as pd
import numpy as np
import re
#from .data_cleaning import extract_data


def normalize_text(text):
    if pd.isna(text):
        return ''
    return re.sub(r'\s+',' ',str(text)).strip()

def combine_text_columns(df):
    df = df.copy()
    df['text'] = (df['Description'] + ' ' + df['Specialities']).apply(normalize_text)
    return df

def extract_binary_features(df):
    df = df.copy()

    df['has_elevator'] = df['text'].str.contains(r'مصعد').astype(int)
    df['has_parking'] = df['text'].str.contains(r'كراج').astype(int)
    df['has_storage'] = df['text'].str.contains(r'مخزن').astype(int)
    df['has_balcony'] = df['text'].str.contains(r'بلكونة|بلكون|بلكونه',regex=True)\
        .astype(int)
    df['has_garden'] = df['text'].str.contains(r'حديقة').astype(int)
    df['has_gym'] = df['text'].str.contains(r'جيم|صالة\s*رياضية|نادي\s*رياضي',regex=True)\
        .astype(int)
    df['has_living_room'] = df['text'].str.contains(r'غرفة\s*معيشة|غرفة\s*معيشه',regex=True)\
        .astype(int)
    df['has_kitchen'] = df['text'].str.contains(r'مطبخ').astype(int)
    df['has_laundry_room'] = df['text'].str.contains(r'غرفة غسيل|غرفة\s*غسيل|غسيل')\
        .astype(int)
    df['has_heating'] = df['text'].str.contains( r'تدفئة|تدفئة\s*مركزية|تدفئة\s*تحت\s*البلاط'\
                                                ,regex=True).astype(int)
    df['has_AC'] = df['text'].str.contains(r'تكييف|تكييف\s*مركزي|وحدات\s*تكييف',regex=True)\
        .astype(int)
    df['has_security_doors'] = df['text'].str.contains\
        ( r'ابواب\s*امان|أبواب\s*أمان|باب\s*امان|باب\s*أمان',regex=True).astype(int)
    return df

def create_numerical_features(df):
    df = df.copy()

    df['Price_per_sqm'] = df['Final_price'].div(df['Area_sqm'],fill_value=np.nan)
    return df

def extract_salons(text):
    if pd.isna(text):
        return 0
    
    patterns = [
        r'(\d+)\s*صالون',
        r'صالون\s*عدد\s*(\d+)'

    ]

    for pattern in patterns:
        match = re.search(pattern,str(text))
        if match:
            return int(match.group(1))
    if re.search(r'\bصالون\b',str(text)):
        return 1
    return 0

def extract_master_bedroom(text):
    if pd.isna(text):
        return 0
    patterns = [
        r'ماستر\s*عدد\s*(\d+)',
        r'(\d+)\s*ماستر',
        r'\((\d+)\s*ماستر\)',
        r'\(ماستر\s*(\d+)\)',
        r'\(ماستر\s*عدد\s*(\d+)\)'
    ]

    for pattern in patterns:
        match = re.search(pattern=pattern,
                          string=str(text))
        if match:
            return int(match.group(1))
    if re.search(pattern=r'غرفة\s*نوم\s*ماستر|نوم\s*ماستر',string=str(text)):
        return 1
    return 0

def extract_advanced_count_features(df):
    df = df.copy()
    df['Salons'] = df['text'].apply(extract_salons)
    df['Master_bedrooms'] = df['text'].apply(extract_master_bedroom)
    return df

def extract_full_location_features(df):
    df = df.copy()
    df[['Area','City','Country']] = df['Location'].str.split(',',expand=True,n=2)
    df['Area'] = df['Area'].str.strip()
    df['City'] = df['City'].str.strip()
    df['Country'] = df['Country'].str.strip()
    return df

def feature_engineering_pipeline(df):
    df = combine_text_columns(df)
    df = extract_binary_features(df)
    df = create_numerical_features(df)
    df = extract_advanced_count_features(df)
    df = extract_full_location_features(df)
    return df




