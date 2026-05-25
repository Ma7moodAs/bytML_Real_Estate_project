# Bayti Backend

FastAPI backend for the Bayti real estate platform.

## Current API

The backend currently serves the scraped apartment inventory and precomputed recommendations from CSV files.

Endpoints:

```text
GET  /api/health
GET  /api/filters
GET  /api/properties
GET  /api/properties/{apartment_id}
GET  /api/properties/{apartment_id}/recommendations
POST /api/properties
```

## Run

From the project root:

```powershell
uvicorn Backend.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Data Source

Current scraped properties:

```text
recommender_system/data/apartments.csv
```

Current recommendation output:

```text
recommender_system/data/precomputed_recommendations.csv
```

User-added properties are temporarily stored in:

```text
recommender_system/data/user_listings.csv
```

This CSV-backed storage is temporary. It can be replaced with a database layer later without changing the API contract.
