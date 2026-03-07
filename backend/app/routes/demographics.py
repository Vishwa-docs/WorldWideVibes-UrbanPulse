"""Demographics endpoints using US Census API."""
from fastapi import APIRouter, HTTPException
from app.services.census_service import get_census_service

router = APIRouter(prefix="/api/demographics", tags=["demographics"])


@router.get("/tract")
async def get_tract_demographics(lat: float, lng: float):
    """Get demographics for the census tract at given coordinates."""
    try:
        service = get_census_service()
        data = await service.get_tract_demographics(lat, lng)
        return data
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch demographics: {str(e)}")


@router.get("/city")
async def get_city_demographics():
    """Get overall Montgomery, AL demographics."""
    try:
        service = get_census_service()
        data = await service.get_city_overview()
        return data
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch city demographics: {str(e)}")


@router.get("/neighborhood")
async def get_neighborhood_demographics(tracts: str):
    """Get demographics for specified census tracts (comma-separated)."""
    tract_list = [t.strip() for t in tracts.split(",") if t.strip()]
    if not tract_list:
        raise HTTPException(400, "Provide at least one tract code")
    try:
        service = get_census_service()
        data = await service.get_neighborhood_demographics(tract_list)
        return data
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch neighborhood demographics: {str(e)}")
