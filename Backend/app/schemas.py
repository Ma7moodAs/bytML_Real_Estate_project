from typing import Optional

from pydantic import BaseModel


class PropertyCreate(BaseModel):
    Listing_type: str
    Bedrooms: int
    Bathrooms: int
    Area_sqm: float
    Furnished: bool
    Pool: bool
    Floor: str
    Floor_type: str
    Location: str
    Description: str
    Specialities: str
    Sale_price: Optional[float] = None
    Price_annualy: Optional[float] = None
    Price_monthly: Optional[float] = None
    URL: Optional[str] = None
