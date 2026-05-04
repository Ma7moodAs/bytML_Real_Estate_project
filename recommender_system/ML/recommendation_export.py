"""Export helpers for precomputed property recommendations."""

from pathlib import Path

import pandas as pd

try:
    from .pipeline import run_recommender_pipeline
    from .recommendation_engine import get_similar_properties
except ImportError:
    import sys

    current_dir = Path(__file__).resolve().parent
    if str(current_dir) not in sys.path:
        sys.path.append(str(current_dir))

    from pipeline import run_recommender_pipeline
    from recommendation_engine import get_similar_properties


EXPORT_COLUMNS = [
    "source_apartment_id",
    "recommended_apartment_id",
    "rank",
    "similarity_score",
]


def build_recommendation_table(
    engineered_df,
    similarity_matrix,
    top_n=5,
    identifier_col="apartment_id",
    prefer_same_area=True,
):
    rows = []

    for source_id in engineered_df[identifier_col].tolist():
        recommendations = get_similar_properties(
            engineered_df=engineered_df,
            similarity_matrix=similarity_matrix,
            item_id=source_id,
            top_n=top_n,
            identifier_col=identifier_col,
            prefer_same_area=prefer_same_area,
            result_columns=[identifier_col],
        )

        for rank, recommendation in enumerate(recommendations.itertuples(index=False), start=1):
            rows.append(
                {
                    "source_apartment_id": source_id,
                    "recommended_apartment_id": getattr(recommendation, identifier_col),
                    "rank": rank,
                    "similarity_score": recommendation.similarity_score,
                }
            )

    return pd.DataFrame(rows, columns=EXPORT_COLUMNS)


def save_recommendation_table(recommendations_df, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    recommendations_df.to_csv(output_path, index=False)
    return output_path


def run_and_export_recommendations(
    input_path,
    output_path,
    mode="legacy",
    top_n=5,
    identifier_col="apartment_id",
    prefer_same_area=True,
    require_identifier=None,
):
    pipeline_result = run_recommender_pipeline(
        file_path=input_path,
        mode=mode,
        identifier_col=identifier_col,
        require_identifier=require_identifier,
    )

    if not pipeline_result["success"]:
        return {
            **pipeline_result,
            "recommendations_df": pd.DataFrame(columns=EXPORT_COLUMNS),
            "output_path": None,
        }

    recommendations_df = build_recommendation_table(
        engineered_df=pipeline_result["engineered_df"],
        similarity_matrix=pipeline_result["similarity_matrix"],
        top_n=top_n,
        identifier_col=identifier_col,
        prefer_same_area=prefer_same_area,
    )
    saved_path = save_recommendation_table(recommendations_df, output_path)

    return {
        **pipeline_result,
        "recommendations_df": recommendations_df,
        "output_path": saved_path,
    }
