"""Walk Score endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models.property import Property
from app.services.walkscore import compute_walk_score

router = APIRouter(prefix="/api/walkscore", tags=["walkscore"])


@router.get("/{property_id}")
async def get_walk_score(property_id: int, session: Session = Depends(get_session)):
    """Compute walk score for a property using real Google Places data."""
    prop = session.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    
    try:
        result = await compute_walk_score(prop.latitude, prop.longitude)
        return {
            "property_id": property_id,
            "address": prop.address,
            "neighborhood": prop.neighborhood,
            **result,
        }
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"Walk score computation failed: {str(e)}")


@router.get("/coordinates/")
async def get_walk_score_by_coords(lat: float, lng: float):
    """Compute walk score for arbitrary coordinates."""
    try:
        result = await compute_walk_score(lat, lng)
        return {"latitude": lat, "longitude": lng, **result}
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"Walk score computation failed: {str(e)}")
