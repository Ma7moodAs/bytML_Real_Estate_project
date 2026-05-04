"""Command-line runner for regenerating precomputed recommendations."""

import argparse
from pathlib import Path

try:
    from .recommendation_export import run_and_export_recommendations
except ImportError:
    import sys

    current_dir = Path(__file__).resolve().parent
    if str(current_dir) not in sys.path:
        sys.path.append(str(current_dir))

    from recommendation_export import run_and_export_recommendations


RECOMMENDER_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = RECOMMENDER_ROOT / "data" / "apartments.csv"
DEFAULT_OUTPUT_PATH = RECOMMENDER_ROOT / "data" / "precomputed_recommendations.csv"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Regenerate offline property recommendations."
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT_PATH,
        type=Path,
        help="Input property dataset path.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH,
        type=Path,
        help="Output recommendations CSV path.",
    )
    parser.add_argument(
        "--mode",
        choices=["legacy", "strict"],
        default="legacy",
        help="Use legacy mode for scraped CSVs or strict mode for validated stored data.",
    )
    parser.add_argument(
        "--top-n",
        default=5,
        type=int,
        help="Maximum number of recommendations per source apartment.",
    )
    parser.add_argument(
        "--identifier-col",
        default="apartment_id",
        help="Property identifier column name.",
    )
    parser.add_argument(
        "--no-prefer-same-area",
        action="store_true",
        help="Disable the same-area candidate preference.",
    )
    parser.add_argument(
        "--require-identifier",
        action="store_true",
        help="Require identifier column during strict validation.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    result = run_and_export_recommendations(
        input_path=args.input,
        output_path=args.output,
        mode=args.mode,
        top_n=args.top_n,
        identifier_col=args.identifier_col,
        prefer_same_area=not args.no_prefer_same_area,
        require_identifier=args.require_identifier if args.require_identifier else None,
    )

    if not result["success"]:
        print("Recommendation batch failed validation.")
        for error in result["errors"]:
            print(f"- {error}")
        raise SystemExit(1)

    recommendations_df = result["recommendations_df"]
    print("Recommendation batch completed.")
    print(f"Mode: {result['mode']}")
    print(f"Source rows: {len(result['source_df'])}")
    print(f"Prepared rows: {len(result['prepared_df'])}")
    print(f"Recommendation rows: {len(recommendations_df)}")
    print(f"Unique source apartments: {recommendations_df['source_apartment_id'].nunique()}")
    print(f"Output: {result['output_path']}")


if __name__ == "__main__":
    main()
