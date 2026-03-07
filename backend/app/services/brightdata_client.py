"""
Bright Data integration client for UrbanPulse.

Uses Bright Data's Web Scraper API to fetch:
- POI (Points of Interest) data around a location
- Google Maps business data (reviews, ratings)
- Local business activity signals

Requires BRIGHTDATA_API_TOKEN to be set. No mock/simulated data.
"""

import httpx
import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)


class BrightDataClient:
    """Client for Bright Data Web Scraper API."""

    def __init__(self):
        self.settings = get_settings()
        self.api_token = self.settings.brightdata_api_token
        self.base_url = self.settings.brightdata_base_url
        if not self.api_token:
            raise RuntimeError(
                "Bright Data API token is not configured. "
                "Set the BRIGHTDATA_API_TOKEN environment variable."
            )
        self.is_configured = True

    async def fetch_pois_near(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.0,
        category: str = "business",
    ) -> dict:
        """Fetch Points of Interest near a coordinate using Bright Data."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                url = f"{self.base_url}/datasets/v3/trigger"
                payload = {
                    "dataset_id": "gd_l1vijqt9jfj7olhj",
                    "url": f"https://www.google.com/maps/search/{category}/@{lat},{lng},15z",
                    "format": "json",
                }
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                }
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return self._parse_brightdata_response(response.json(), category)
        except Exception as e:
            logger.error("Bright Data POI fetch failed: %s", e)
            return {
                "total_count": 0,
                "competitor_count": 0,
                "category": category,
                "source": "brightdata",
                "pois": [],
                "error": str(e),
            }

    async def fetch_reviews_near(
        self, lat: float, lng: float, business_type: str = "restaurant"
    ) -> dict:
        """Fetch review data for businesses near a location."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                url = f"{self.base_url}/datasets/v3/trigger"
                payload = {
                    "dataset_id": "gd_l1vijqt9jfj7olhj",
                    "url": f"https://www.google.com/maps/search/{business_type}/@{lat},{lng},15z",
                    "format": "json",
                }
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                }
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return self._parse_review_response(response.json(), business_type)
        except Exception as e:
            logger.error("Bright Data review fetch failed: %s", e)
            return {
                "avg_rating": 0,
                "total_reviews": 0,
                "business_type": business_type,
                "source": "brightdata",
                "error": str(e),
            }

    async def fetch_activity_signals(
        self, lat: float, lng: float, radius_km: float = 0.5
    ) -> dict:
        """
        Aggregate activity signals for a location.
        Returns poi_count, avg_rating, review_count, competitor_count, activity_index.
        """
        pois = await self.fetch_pois_near(lat, lng, radius_km)
        reviews = await self.fetch_reviews_near(lat, lng)

        poi_count = pois.get("total_count", 0)
        avg_rating = reviews.get("avg_rating", 0)
        review_count = reviews.get("total_reviews", 0)
        competitor_count = pois.get("competitor_count", 0)

        # Compute activity index (0-10)
        activity_index = min(
            10.0,
            (
                (min(poi_count, 50) / 50) * 3
                + (avg_rating / 5) * 3
                + (min(review_count, 500) / 500) * 2
                + (1 - min(competitor_count, 20) / 20) * 2
            ),
        )

        return {
            "poi_count": poi_count,
            "avg_rating": round(avg_rating, 2),
            "review_count": review_count,
            "competitor_count": competitor_count,
            "activity_index": round(activity_index, 2),
            "source": "brightdata",
        }

    def _parse_brightdata_response(self, data: dict, category: str) -> dict:
        """Parse actual Bright Data API response into our format."""
        results = data.get("results", data.get("data", []))
        if isinstance(results, list):
            return {
                "total_count": len(results),
                "competitor_count": len(
                    [
                        r
                        for r in results
                        if r.get("category", "").lower() == category.lower()
                    ]
                ),
                "category": category,
                "source": "brightdata",
                "pois": results[:10],
            }
        return {
            "total_count": 0,
            "competitor_count": 0,
            "category": category,
            "source": "brightdata",
            "pois": [],
        }

    def _parse_review_response(self, data: dict, business_type: str) -> dict:
        """Parse actual Bright Data review response."""
        results = data.get("results", data.get("data", []))
        if isinstance(results, list) and results:
            ratings = [r.get("rating", 0) for r in results if r.get("rating")]
            reviews = [
                r.get("review_count", 0) for r in results if r.get("review_count")
            ]
            return {
                "avg_rating": (
                    round(sum(ratings) / len(ratings), 2) if ratings else 0
                ),
                "total_reviews": sum(reviews) if reviews else 0,
                "business_type": business_type,
                "source": "brightdata",
            }
        return {
            "avg_rating": 0,
            "total_reviews": 0,
            "business_type": business_type,
            "source": "brightdata",
        }


# Singleton instance
_client: Optional[BrightDataClient] = None


def get_brightdata_client() -> BrightDataClient:
    global _client
    if _client is None:
        _client = BrightDataClient()
    return _client
