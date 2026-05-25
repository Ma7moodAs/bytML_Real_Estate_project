from pathlib import Path

import pandas as pd

from recommender_system.ML.data_validation import validate_property_data
from recommender_system.ML.pipeline import prepare_property_inventory, run_recommender_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RECOMMENDER_DATA_DIR = PROJECT_ROOT / "recommender_system" / "data"
SCRAPED_DATA_PATH = RECOMMENDER_DATA_DIR / "apartments.csv"
RECOMMENDATIONS_PATH = RECOMMENDER_DATA_DIR / "precomputed_recommendations.csv"
USER_LISTINGS_PATH = RECOMMENDER_DATA_DIR / "user_listings.csv"

_INVENTORY_CACHE = None
_RECOMMENDATIONS_CACHE = None


def _to_python_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def _row_to_dict(row):
    return {key: _to_python_value(value) for key, value in row.to_dict().items()}


def clear_cache():
    global _INVENTORY_CACHE, _RECOMMENDATIONS_CACHE
    _INVENTORY_CACHE = None
    _RECOMMENDATIONS_CACHE = None


def _load_scraped_inventory():
    result = run_recommender_pipeline(SCRAPED_DATA_PATH, mode="legacy")
    if not result["success"]:
        raise RuntimeError(f"Failed to load scraped inventory: {result['errors']}")
    return result["engineered_df"]


def _load_user_inventory():
    if not USER_LISTINGS_PATH.exists():
        return pd.DataFrame()

    user_df = pd.read_csv(USER_LISTINGS_PATH)
    if user_df.empty:
        return pd.DataFrame()

    result = prepare_property_inventory(
        user_df,
        mode="strict",
        require_identifier=True,
    )
    if not result["success"]:
        raise RuntimeError(f"User listing data failed validation: {result['errors']}")
    return result["engineered_df"]


def load_inventory():
    global _INVENTORY_CACHE

    if _INVENTORY_CACHE is not None:
        return _INVENTORY_CACHE.copy()

    scraped_df = _load_scraped_inventory()
    user_df = _load_user_inventory()

    if user_df.empty:
        inventory_df = scraped_df
    else:
        inventory_df = pd.concat([scraped_df, user_df], ignore_index=True, sort=False)

    _INVENTORY_CACHE = inventory_df.reset_index(drop=True)
    return _INVENTORY_CACHE.copy()


def load_recommendations():
    global _RECOMMENDATIONS_CACHE

    if _RECOMMENDATIONS_CACHE is not None:
        return _RECOMMENDATIONS_CACHE.copy()

    if not RECOMMENDATIONS_PATH.exists():
        _RECOMMENDATIONS_CACHE = pd.DataFrame(
            columns=[
                "source_apartment_id",
                "recommended_apartment_id",
                "rank",
                "similarity_score",
            ]
        )
    else:
        _RECOMMENDATIONS_CACHE = pd.read_csv(RECOMMENDATIONS_PATH)

    return _RECOMMENDATIONS_CACHE.copy()


def get_next_apartment_id():
    inventory_df = load_inventory()
    if inventory_df.empty or "apartment_id" not in inventory_df.columns:
        return 1
    return int(pd.to_numeric(inventory_df["apartment_id"], errors="coerce").max()) + 1


def validate_new_listing(row):
    validation_df = pd.DataFrame([row])
    return validate_property_data(validation_df, require_identifier=True)


def save_user_listing(row):
    USER_LISTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    new_row_df = pd.DataFrame([row])
    if USER_LISTINGS_PATH.exists():
        existing_df = pd.read_csv(USER_LISTINGS_PATH)
        updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
    else:
        updated_df = new_row_df

    updated_df.to_csv(USER_LISTINGS_PATH, index=False)
    clear_cache()
    return row["apartment_id"]


def get_property(apartment_id):
    inventory_df = load_inventory()
    matches = inventory_df[inventory_df["apartment_id"] == apartment_id]
    if matches.empty:
        return None
    return _row_to_dict(matches.iloc[0])


def list_properties(listing_type=None, area=None, limit=24, offset=0):
    inventory_df = load_inventory()

    if listing_type:
        inventory_df = inventory_df[inventory_df["Listing_type"] == listing_type]

    if area:
        inventory_df = inventory_df[inventory_df["Area"] == area]

    total = len(inventory_df)
    page_df = inventory_df.iloc[offset : offset + limit]
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [_row_to_dict(row) for _, row in page_df.iterrows()],
    }


def list_filters():
    inventory_df = load_inventory()
    areas = sorted(value for value in inventory_df["Area"].dropna().unique().tolist())
    listing_types = sorted(value for value in inventory_df["Listing_type"].dropna().unique().tolist())
    return {
        "listing_types": listing_types,
        "areas": areas,
    }


def list_recommendations(apartment_id, limit=5):
    inventory_df = load_inventory()
    recommendations_df = load_recommendations()

    matches = recommendations_df[
        recommendations_df["source_apartment_id"] == apartment_id
    ].sort_values("rank")
    matches = matches.head(limit)

    results = []
    for _, recommendation in matches.iterrows():
        recommended_id = int(recommendation["recommended_apartment_id"])
        property_matches = inventory_df[inventory_df["apartment_id"] == recommended_id]
        if property_matches.empty:
            continue

        item = _row_to_dict(property_matches.iloc[0])
        item["rank"] = int(recommendation["rank"])
        item["similarity_score"] = float(recommendation["similarity_score"])
        results.append(item)

    return results
