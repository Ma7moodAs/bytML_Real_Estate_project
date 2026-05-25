# Bayti Frontend

Static frontend MVP for the Bayti real estate platform.

## Screens

- Main listings page
- Listing type and area filters
- Property details view
- Recommendation section on the details view
- Add listing form

## Run

Start the backend first from the project root:

```powershell
uvicorn Backend.app.main:app --reload
```

Then open:

```text
Frontend/index.html
```

The frontend calls the backend at:

```text
http://127.0.0.1:8000/api
```

## Backend Endpoints Used

```text
GET  /api/filters
GET  /api/properties
GET  /api/properties/{apartment_id}
GET  /api/properties/{apartment_id}/recommendations
POST /api/properties
```
