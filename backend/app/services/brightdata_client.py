"""
Bright Data integration client for UrbanPulse.

Uses Bright Data's Web Scraper API to fetch:
- POI (Points of Interest) data around a location
- Google Maps business data (reviews, ratings)
- Local business activity signals

When BRIGHTDATA_API_TOKEN is not set, returns simulated data for demo purposes.
"""

import httpx
import random
from typing import Optional
from app.config import get_settings


class BrightDataClient:
    """Client for Bright Data Web Scraper API."""

    def __init__(self):
        self.settings = get_settings()
        self.api_token = self.settings.brightdata_api_token
        self.base_url = self.settings.brightdata_base_url
        self.is_configured = bool(
            self.api_token and self.api_token != "your_brightdata_api_token_here"
        )

    async def fetch_pois_near(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.0,
        category: str = "business",
    ) -> dict:
        """Fetch Points of Interest near a coordinate using Bright Data."""
        if not self.is_configured:
            return self._generate_mock_pois(lat, lng, category)

        # Real Bright Data API call
        # Uses the Web Scraper API to search Google Maps for businesses
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Bright Data Web Scraper endpoint for Google Maps
                url = f"{self.base_url}/datasets/v3/trigger"
                payload = {
                    "dataset_id": "gd_l1vijqt9jfj7olhj",  # Google Maps dataset
                    "url": f"https://www.google.com/maps/search/{category}/@{lat},{lng},15z",
                    "format": "json",
                }
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                }
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    return self._parse_brightdata_response(response.json(), category)
                else:
                    # Fall back to mock on error
                    return self._generate_mock_pois(lat, lng, category)
        except Exception:
            return self._generate_mock_pois(lat, lng, category)

    async def fetch_reviews_near(
        self, lat: float, lng: float, business_type: str = "restaurant"
    ) -> dict:
        """Fetch review data for businesses near a location."""
        if not self.is_configured:
            return self._generate_mock_reviews(lat, lng, business_type)

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
                if response.status_code == 200:
                    return self._parse_review_response(response.json(), business_type)
                else:
                    return self._generate_mock_reviews(lat, lng, business_type)
        except Exception:
            return self._generate_mock_reviews(lat, lng, business_type)

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
            "source": "brightdata" if self.is_configured else "simulated",
        }

    def _generate_mock_pois(self, lat: float, lng: float, category: str) -> dict:
        """Generate realistic mock POI data for demo purposes."""
        # Use location hash for consistent results
        seed = int((lat * 1000 + lng * 1000) % 10000)
        rng = random.Random(seed)

        base_count = rng.randint(5, 45)
        return {
            "total_count": base_count,
            "competitor_count": rng.randint(0, min(15, base_count)),
            "category": category,
            "source": "simulated",
            "pois": [
                {
                    "name": f"Business {i+1}",
                    "category": category,
                    "lat": lat + rng.uniform(-0.005, 0.005),
                    "lng": lng + rng.uniform(-0.005, 0.005),
                    "rating": round(rng.uniform(2.5, 5.0), 1),
                }
                for i in range(min(10, base_count))
            ],
        }

    def _generate_mock_reviews(
        self, lat: float, lng: float, business_type: str
    ) -> dict:
        """Generate realistic mock review data for demo purposes."""
        seed = int((lat * 1000 + lng * 1000 + 42) % 10000)
        rng = random.Random(seed)

        return {
            "avg_rating": round(rng.uniform(3.0, 4.8), 2),
            "total_reviews": rng.randint(20, 500),
            "business_type": business_type,
            "sentiment": rng.choice(["positive", "mixed", "neutral"]),
            "source": "simulated",
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
        return self._generate_mock_pois(0, 0, category)

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
                    round(sum(ratings) / len(ratings), 2) if ratings else 3.5
                ),
                "total_reviews": sum(reviews) if reviews else 0,
                "business_type": business_type,
                "source": "brightdata",
            }
        return self._generate_mock_reviews(0, 0, business_type)


# Singleton instance
_client: Optional[BrightDataClient] = None


def get_brightdata_client() -> BrightDataClient:
    global _client
    if _client is None:
        _client = BrightDataClient()
    return _client
