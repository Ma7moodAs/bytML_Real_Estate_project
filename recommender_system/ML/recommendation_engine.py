import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

try:
    from .data_cleaning import clean_data
    from .feature_engineering import feature_engineering_pipeline
    from .data_preprocessing import prepare_recommender_inputs
except ImportError:
    import sys
    from pathlib import Path

    current_dir = Path(__file__).resolve().parent
    if str(current_dir) not in sys.path:
        sys.path.append(str(current_dir))

    from data_cleaning import clean_data
    from feature_engineering import feature_engineering_pipeline
    from data_preprocessing import prepare_recommender_inputs


DEFAULT_RESULT_COLUMNS = [
    "apartment_id",
    "Listing_type",
    "Area",
    "City",
    "Bedrooms",
    "Bathrooms",
    "Area_sqm",
    "Final_price",
    "Price_per_sqm",
]


def ensure_identifier(df, identifier_col="apartment_id"):
    df = df.copy()

    if identifier_col not in df.columns:
        df[identifier_col] = range(1, len(df) + 1)

    return df


def build_recommender_artifacts(df, identifier_col="apartment_id", excluded_columns=None):
    cleaned_df = clean_data(df)
    cleaned_df = ensure_identifier(cleaned_df, identifier_col=identifier_col).reset_index(drop=True)

    engineered_df = feature_engineering_pipeline(cleaned_df)
    recommender_inputs = prepare_recommender_inputs(
        engineered_df,
        excluded_columns=excluded_columns,
        identifier_col=identifier_col,
    )

    similarity_matrix = cosine_similarity(recommender_inputs["X_preprocessed"])

    return {
        "cleaned_df": cleaned_df,
        "engineered_df": engineered_df,
        "similarity_matrix": similarity_matrix,
        **recommender_inputs,
    }


def _same_listing_type_candidates(df, source_row):
    return df["Listing_type"] == source_row["Listing_type"]


def _same_area_candidates(df, source_row):
    return _same_listing_type_candidates(df, source_row) & (df["Area"] == source_row["Area"])


def _same_city_candidates(df, source_row):
    return _same_listing_type_candidates(df, source_row) & (df["City"] == source_row["City"])


def get_candidate_mask(df, source_index, prefer_same_area=True):
    source_row = df.loc[source_index]
    base_mask = _same_listing_type_candidates(df, source_row)

    if not prefer_same_area:
        return base_mask

    area_mask = _same_area_candidates(df, source_row)
    if area_mask.sum() > 1:
        return area_mask

    city_mask = _same_city_candidates(df, source_row)
    if city_mask.sum() > 1:
        return city_mask

    return base_mask


def _resolve_source_index(df, item_id, identifier_col="apartment_id"):
    matches = df.index[df[identifier_col] == item_id]
    if len(matches) == 0:
        raise ValueError(f"{identifier_col}={item_id} was not found in the dataset.")
    return matches[0]


def get_similar_properties(
    engineered_df,
    similarity_matrix,
    item_id,
    top_n=5,
    identifier_col="apartment_id",
    prefer_same_area=True,
    result_columns=None,
):
    source_index = _resolve_source_index(engineered_df, item_id, identifier_col=identifier_col)
    candidate_mask = get_candidate_mask(engineered_df, source_index, prefer_same_area=prefer_same_area)
    candidate_indices = engineered_df.index[candidate_mask].tolist()

    if source_index in candidate_indices:
        candidate_indices.remove(source_index)

    if not candidate_indices:
        return pd.DataFrame(columns=(result_columns or DEFAULT_RESULT_COLUMNS) + ["similarity_score"])

    scores = [
        (candidate_index, similarity_matrix[source_index, candidate_index])
        for candidate_index in candidate_indices
    ]
    scores.sort(key=lambda item: item[1], reverse=True)
    top_matches = scores[:top_n]

    result_columns = result_columns or DEFAULT_RESULT_COLUMNS
    available_columns = [col for col in result_columns if col in engineered_df.columns]
    result_indices = [match_index for match_index, _ in top_matches]

    recommendations = engineered_df.loc[result_indices, available_columns].copy()
    recommendations["similarity_score"] = [score for _, score in top_matches]

    return recommendations.reset_index(drop=True)


