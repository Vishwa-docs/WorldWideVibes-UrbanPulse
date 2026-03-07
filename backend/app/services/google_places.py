"""
Google Places API service.

Fetches real POI (Points of Interest) data using the googlemaps library.
All network calls are executed via ``asyncio.to_thread`` so the async
FastAPI event-loop is never blocked.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import googlemaps

from app.config import get_settings

logger = logging.getLogger(__name__)


class GooglePlacesService:
    """Thin async wrapper around the *googlemaps* client."""

    def __init__(self) -> None:
        api_key = get_settings().google_places_api_key
        if not api_key:
            raise RuntimeError(
                "Google Places API key is not configured. "
                "Set the GOOGLE_PLACES_API_KEY environment variable."
            )
        self._client = googlemaps.Client(key=api_key)

    # ── public methods ────────────────────────────────────────────────────

    async def nearby_pois(
        self,
        lat: float,
        lng: float,
        radius_m: int = 1000,
        place_type: str = "store",
    ) -> dict[str, Any]:
        """Return nearby places of a given *place_type*.

        Returns a dict with ``"results"`` (list of place summaries) and
        ``"total"`` (count).
        """
        try:
            response = await asyncio.to_thread(
                self._client.places_nearby,
                location=(lat, lng),
                radius=radius_m,
                type=place_type,
            )
            results = response.get("results", [])
            return {
                "results": [
                    {
                        "place_id": p.get("place_id"),
                        "name": p.get("name"),
                        "vicinity": p.get("vicinity"),
                        "rating": p.get("rating"),
                        "user_ratings_total": p.get("user_ratings_total", 0),
                        "types": p.get("types", []),
                        "location": p.get("geometry", {}).get("location"),
                        "business_status": p.get("business_status"),
                    }
                    for p in results
                ],
                "total": len(results),
            }
        except Exception:
            logger.exception("nearby_pois failed (lat=%s, lng=%s)", lat, lng)
            return {"results": [], "total": 0, "error": "Failed to fetch nearby POIs"}

    async def place_details(self, place_id: str) -> dict[str, Any]:
        """Fetch detailed information for a single place.

        Returns rating, review count, price level, opening hours and types.
        """
        fields = [
            "rating",
            "user_ratings_total",
            "price_level",
            "opening_hours",
            "types",
            "name",
            "formatted_address",
            "business_status",
        ]
        try:
            response = await asyncio.to_thread(
                self._client.place,
                place_id,
                fields=fields,
            )
            result = response.get("result", {})
            return {
                "place_id": place_id,
                "name": result.get("name"),
                "formatted_address": result.get("formatted_address"),
                "rating": result.get("rating"),
                "user_ratings_total": result.get("user_ratings_total", 0),
                "price_level": result.get("price_level"),
                "opening_hours": result.get("opening_hours"),
                "types": result.get("types", []),
                "business_status": result.get("business_status"),
            }
        except Exception:
            logger.exception("place_details failed (place_id=%s)", place_id)
            return {"place_id": place_id, "error": "Failed to fetch place details"}

    async def nearby_competitors(
        self,
        lat: float,
        lng: float,
        business_type: str = "grocery_or_supermarket",
        radius_m: int = 1500,
    ) -> dict[str, Any]:
        """Count and list competitors of a given *business_type* nearby."""
        try:
            response = await asyncio.to_thread(
                self._client.places_nearby,
                location=(lat, lng),
                radius=radius_m,
                type=business_type,
            )
            results = response.get("results", [])
            competitors = [
                {
                    "place_id": p.get("place_id"),
                    "name": p.get("name"),
                    "vicinity": p.get("vicinity"),
                    "rating": p.get("rating"),
                    "user_ratings_total": p.get("user_ratings_total", 0),
                    "location": p.get("geometry", {}).get("location"),
                }
                for p in results
            ]
            avg_rating = (
                sum(c["rating"] for c in competitors if c["rating"] is not None)
                / max(1, sum(1 for c in competitors if c["rating"] is not None))
            )
            return {
                "competitors": competitors,
                "count": len(competitors),
                "average_rating": round(avg_rating, 2),
                "radius_m": radius_m,
                "business_type": business_type,
            }
        except Exception:
            logger.exception(
                "nearby_competitors failed (lat=%s, lng=%s, type=%s)",
                lat,
                lng,
                business_type,
            )
            return {
                "competitors": [],
                "count": 0,
                "error": "Failed to fetch competitor data",
            }

    async def compute_area_activity(
        self,
        lat: float,
        lng: float,
        radius_m: int = 1000,
    ) -> dict[str, Any]:
        """Aggregate activity metrics for an area.

        Queries several place categories and returns totals, average rating,
        and a per-category breakdown.
        """
        categories = [
            "restaurant",
            "store",
            "cafe",
            "gym",
            "bank",
            "school",
        ]
        breakdown: dict[str, int] = {}
        all_ratings: list[float] = []
        total_places = 0

        for category in categories:
            try:
                response = await asyncio.to_thread(
                    self._client.places_nearby,
                    location=(lat, lng),
                    radius=radius_m,
                    type=category,
                )
                results = response.get("results", [])
                count = len(results)
                breakdown[category] = count
                total_places += count
                all_ratings.extend(
                    p["rating"] for p in results if p.get("rating") is not None
                )
            except Exception:
                logger.exception(
                    "compute_area_activity: category '%s' failed", category
                )
                breakdown[category] = 0

        avg_rating = (
            round(sum(all_ratings) / len(all_ratings), 2) if all_ratings else None
        )

        return {
            "total_places": total_places,
            "average_rating": avg_rating,
            "category_breakdown": breakdown,
            "radius_m": radius_m,
            "categories_queried": categories,
        }


# ── singleton factory ─────────────────────────────────────────────────────

_instance: GooglePlacesService | None = None


def get_google_places_service() -> GooglePlacesService:
    """Return (or create) the singleton ``GooglePlacesService`` instance."""
    global _instance  # noqa: PLW0603
    if _instance is None:
        _instance = GooglePlacesService()
    return _instance
