import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DEFAULT_EXCLUDED_COLUMNS = [
    "URL",
    "Location",
    "Description",
    "Specialities",
    "Country",
    "text",
    "apartment_id",
]


def feature_selection(df, excluded_columns=None):
    excluded_columns = excluded_columns or DEFAULT_EXCLUDED_COLUMNS
    feature_columns = [col for col in df.columns if col not in excluded_columns]
    return df[feature_columns].copy(), feature_columns


def split_features_dtypes(X):
    numeric_columns = X.select_dtypes(include=np.number).columns.to_list()
    categorical_columns = X.select_dtypes(exclude=np.number).columns.to_list()

    binary_columns = [col for col in numeric_columns if X[col].nunique() == 2]
    non_binary_numeric_columns = [col for col in numeric_columns if col not in binary_columns]

    return {
        "numerical_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "binary_columns": binary_columns,
        "non_binary_numeric_columns": non_binary_numeric_columns,
    }


def preprocess_features(X, scaler=None, encoder=None):
    X_scaled = X.copy()
    scaler = scaler or StandardScaler()
    encoder = encoder or OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    feature_groups = split_features_dtypes(X_scaled)
    non_binary_numeric_columns = feature_groups["non_binary_numeric_columns"]
    categorical_columns = feature_groups["categorical_columns"]
    binary_columns = feature_groups["binary_columns"]

    if non_binary_numeric_columns:
        X_scaled[non_binary_numeric_columns] = scaler.fit_transform(X_scaled[non_binary_numeric_columns])

    if categorical_columns:
        encoded_array = encoder.fit_transform(X_scaled[categorical_columns])
        encoded_df = pd.DataFrame(
            encoded_array,
            columns=encoder.get_feature_names_out(categorical_columns),
            index=X_scaled.index,
        )
    else:
        encoded_df = pd.DataFrame(index=X_scaled.index)

    X_preprocessed = pd.concat(
        [
            X_scaled[non_binary_numeric_columns],
            encoded_df,
            X_scaled[binary_columns],
        ],
        axis=1,
    )

    return {
        "X_preprocessed": X_preprocessed,
        "X_selected": X,
        "X_scaled": X_scaled,
        "scaler": scaler,
        "encoder": encoder,
        **feature_groups,
    }


def prepare_recommender_inputs(
    df,
    excluded_columns=None,
    identifier_col="apartment_id",
):
    if identifier_col in df.columns:
        item_ids = df[identifier_col].copy()
    else:
        item_ids = pd.Series(df.index, index=df.index, name="item_id")

    X, feature_columns = feature_selection(df, excluded_columns=excluded_columns)
    preprocessed = preprocess_features(X)
    preprocessed["item_ids"] = item_ids
    preprocessed["feature_columns"] = feature_columns
    return preprocessed
