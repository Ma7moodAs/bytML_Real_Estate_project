# The purpose of this file is only to load the property data and prepare it
# for the recommendation engine pipeline.
# the data will be loaded from a csv file for now, and after the backend team stores
#  the data in the website database, it will load the data from the database by 
# exporting it to a csv file and loading it from there.

import pandas as pd 

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return None