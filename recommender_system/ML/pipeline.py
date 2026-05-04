"""Pipeline orchestration for the recommender system."""

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

try:
    from .data_loader import load_data
    from .data_validation import validate_property_data
    from .data_cleaning import clean_data, fix_dtypes
    from .feature_engineering import feature_engineering_pipeline
    from .data_preprocessing import prepare_recommender_inputs
    from .recommendation_engine import ensure_identifier
except ImportError:
    import sys
    from pathlib import Path

    current_dir = Path(__file__).resolve().parent
    if str(current_dir) not in sys.path:
        sys.path.append(str(current_dir))

    from data_loader import load_data
    from data_validation import validate_property_data
    from data_cleaning import clean_data, fix_dtypes
    from feature_engineering import feature_engineering_pipeline
    from data_preprocessing import prepare_recommender_inputs
    from recommendation_engine import ensure_identifier


SUPPORTED_MODES = {"legacy", "strict"}


def load_input_data(file_path):
    df = load_data(file_path)
    if df is None:
        raise ValueError(f"Failed to load data from: {file_path}")
    return df



def validate_strict_input(df, require_identifier=True):
    return validate_property_data(df, require_identifier=require_identifier)



def _prepare_strict_inventory(df, identifier_col="apartment_id"):
    prepared_df = ensure_identifier(df.copy(), identifier_col=identifier_col).reset_index(drop=True)
    prepared_df["Description"] = prepared_df["Description"].fillna("")
    prepared_df["Specialities"] = prepared_df["Specialities"].fillna("")
    prepared_df["Final_price"] = prepared_df["Sale_price"].where(
        prepared_df["Listing_type"] == "sale",
        prepared_df["Price_annualy"],
    )
    prepared_df = prepared_df.drop(
        columns=["Price_annualy", "Sale_price", "URL", "Price_monthly"],
        errors="ignore",
    )
    prepared_df = fix_dtypes(prepared_df)
    return prepared_df



def _build_artifacts_from_inventory(prepared_df, identifier_col="apartment_id", excluded_columns=None):
    engineered_df = feature_engineering_pipeline(prepared_df)
    recommender_inputs = prepare_recommender_inputs(
        engineered_df,
        excluded_columns=excluded_columns,
        identifier_col=identifier_col,
    )
    similarity_matrix = cosine_similarity(recommender_inputs["X_preprocessed"])

    return {
        "prepared_df": prepared_df,
        "engineered_df": engineered_df,
        "similarity_matrix": similarity_matrix,
        **recommender_inputs,
    }



def prepare_property_inventory(
    df,
    mode="legacy",
    identifier_col="apartment_id",
    excluded_columns=None,
    require_identifier=None,
):
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mode: {mode}. Expected one of {sorted(SUPPORTED_MODES)}")

    require_identifier = (mode == "strict") if require_identifier is None else require_identifier

    if mode == "strict":
        validation = validate_strict_input(df, require_identifier=require_identifier)
        if not validation["is_valid"]:
            return {
                "success": False,
                "mode": mode,
                "validation": validation,
                "errors": validation["errors"],
            }

        prepared_df = _prepare_strict_inventory(df, identifier_col=identifier_col)
    else:
        prepared_df = clean_data(df)
        prepared_df = ensure_identifier(prepared_df, identifier_col=identifier_col).reset_index(drop=True)
        validation = None

    artifacts = _build_artifacts_from_inventory(
        prepared_df,
        identifier_col=identifier_col,
        excluded_columns=excluded_columns,
    )

    return {
        "success": True,
        "mode": mode,
        "validation": validation,
        "errors": [],
        **artifacts,
    }



def run_recommender_pipeline(
    file_path,
    mode="legacy",
    identifier_col="apartment_id",
    excluded_columns=None,
    require_identifier=None,
):
    source_df = load_input_data(file_path)
    pipeline_result = prepare_property_inventory(
        source_df,
        mode=mode,
        identifier_col=identifier_col,
        excluded_columns=excluded_columns,
        require_identifier=require_identifier,
    )
    pipeline_result["source_df"] = source_df
    return pipeline_result
