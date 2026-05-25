from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .data_store import (
    get_next_apartment_id,
    get_property,
    list_filters,
    list_properties,
    list_recommendations,
    save_user_listing,
    validate_new_listing,
)
from .schemas import PropertyCreate


app = FastAPI(title="Bayti Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/filters")
def get_filters():
    return list_filters()


@app.get("/api/properties")
def get_properties(
    listing_type: str | None = Query(default=None, pattern="^(rent|sale)$"),
    area: str | None = None,
    limit: int = Query(default=100, ge=1, le=2000),
    offset: int = Query(default=0, ge=0),
):
    return list_properties(
        listing_type=listing_type,
        area=area,
        limit=limit,
        offset=offset,
    )


@app.get("/api/properties/{apartment_id}")
def get_property_details(apartment_id: int):
    property_item = get_property(apartment_id)
    if property_item is None:
        raise HTTPException(status_code=404, detail="Property not found.")
    return property_item


@app.get("/api/properties/{apartment_id}/recommendations")
def get_property_recommendations(
    apartment_id: int,
    limit: int = Query(default=5, ge=1, le=20),
):
    if get_property(apartment_id) is None:
        raise HTTPException(status_code=404, detail="Property not found.")

    return {
        "source_apartment_id": apartment_id,
        "items": list_recommendations(apartment_id, limit=limit),
    }


@app.post("/api/properties", status_code=201)
def create_property(payload: PropertyCreate):
    row = _model_to_dict(payload)
    row["apartment_id"] = get_next_apartment_id()

    validation = validate_new_listing(row)
    if not validation["is_valid"]:
        raise HTTPException(
            status_code=422,
            detail={"errors": validation["errors"]},
        )

    apartment_id = save_user_listing(row)
    property_item = get_property(apartment_id)
    if property_item is None:
        raise HTTPException(status_code=500, detail="Property was saved but could not be loaded.")

    return property_item
