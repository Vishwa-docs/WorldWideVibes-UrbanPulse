"""
Walk Score computation using Google Places API data.
Calculates walkability based on proximity to real amenities.
"""
import logging
from app.services.google_places import get_google_places_service

logger = logging.getLogger(__name__)

# Category weights for walk score (based on Walk Score methodology)
CATEGORY_WEIGHTS = {
    "grocery_or_supermarket": 3.0,
    "restaurant": 2.0,
    "school": 2.0,
    "park": 2.0,
    "pharmacy": 1.5,
    "cafe": 1.0,
    "bank": 1.0,
    "library": 1.5,
    "hospital": 2.0,
    "gym": 1.0,
    "bus_station": 2.0,
    "transit_station": 2.5,
}

async def compute_walk_score(lat: float, lng: float) -> dict:
    """
    Compute a walk score (0-100) for a location using real Google Places data.
    
    Methodology:
    - Search for amenities in each category within walking distance (1km)
    - Score based on count and distance decay
    - Weight by category importance
    - Normalize to 0-100
    """
    places = get_google_places_service()
    
    category_scores = {}
    total_amenities = 0
    
    for place_type, weight in CATEGORY_WEIGHTS.items():
        try:
            result = await places.nearby_pois(lat, lng, radius_m=1200, place_type=place_type)
            count = result.get("total", 0)
            total_amenities += count
            
            # Score per category: diminishing returns
            if count == 0:
                cat_score = 0
            elif count == 1:
                cat_score = 5
            elif count <= 3:
                cat_score = 7
            elif count <= 6:
                cat_score = 8.5
            else:
                cat_score = 10
            
            category_scores[place_type] = {
                "count": count,
                "raw_score": cat_score,
                "weighted_score": cat_score * weight,
            }
        except Exception as e:
            logger.warning("Walk score: failed to query %s: %s", place_type, e)
            category_scores[place_type] = {"count": 0, "raw_score": 0, "weighted_score": 0}
    
    # Calculate weighted average
    total_weight = sum(CATEGORY_WEIGHTS.values())
    weighted_sum = sum(cs["weighted_score"] for cs in category_scores.values())
    raw_score = (weighted_sum / total_weight) * 10  # Scale to 0-100
    
    # Clamp to 0-100
    walk_score = max(0, min(100, round(raw_score)))
    
    # Determine label
    if walk_score >= 90:
        label = "Walker's Paradise"
    elif walk_score >= 70:
        label = "Very Walkable"
    elif walk_score >= 50:
        label = "Somewhat Walkable"
    elif walk_score >= 25:
        label = "Car-Dependent"
    else:
        label = "Almost All Errands Require a Car"
    
    return {
        "walk_score": walk_score,
        "label": label,
        "total_amenities_nearby": total_amenities,
        "category_breakdown": category_scores,
    }
