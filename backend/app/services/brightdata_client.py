"""
Bright Data integration client for UrbanPulse.

Supports four Bright Data products:
1. Web Scraper (Datasets API)  — Google Maps POIs & reviews
2. SERP API                    — Local search engine results
3. Web Unlocker                — Scrape any public page as clean markdown
4. MCP Server                  — AI agent integration (documented, not called directly)

Modes:
- Live mode (API token configured): calls Bright Data endpoints
- Fallback mode (no token): deterministic simulated signals for robust demos
"""

import hashlib
import logging
import re
from datetime import datetime, timezone
from random import Random
from typing import Optional
from urllib.parse import quote_plus

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class BrightDataClient:
    """Client for Bright Data Web Scraper, SERP API, and Web Unlocker."""

    def __init__(self, strict: bool = True):
        self.settings = get_settings()
        self.api_token = self.settings.brightdata_api_token
        self.base_url = self.settings.brightdata_base_url
        self.serp_zone = self.settings.brightdata_serp_zone
        self.unlocker_zone = self.settings.brightdata_unlocker_zone
        self.is_configured = bool(self.api_token)
        if strict and not self.api_token:
            raise RuntimeError(
                "Bright Data API token is not configured. "
                "Set the BRIGHTDATA_API_TOKEN environment variable."
            )
        if not self.is_configured:
            logger.warning(
                "Bright Data token is missing. Falling back to simulated web signals."
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
            return self._simulate_poi_response(lat, lng, category)

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
            simulated = self._simulate_poi_response(lat, lng, category)
            simulated["error"] = str(e)
            simulated["source"] = "brightdata_simulated_after_error"
            return simulated

    async def fetch_reviews_near(
        self, lat: float, lng: float, business_type: str = "restaurant"
    ) -> dict:
        """Fetch review data for businesses near a location."""
        if not self.is_configured:
            return self._simulate_review_response(lat, lng, business_type)

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
            simulated = self._simulate_review_response(lat, lng, business_type)
            simulated["error"] = str(e)
            simulated["source"] = "brightdata_simulated_after_error"
            return simulated

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
            "source": "brightdata" if self.is_configured else "brightdata_simulated",
            "is_live": self.is_configured,
            "ttl_seconds": 3600,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
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

    # ── SERP API ──────────────────────────────────────────────────────────

    async def search_serp(
        self,
        query: str,
        engine: str = "google",
        location: str = "Montgomery,Alabama,United States",
        num_results: int = 10,
    ) -> dict:
        """
        Search via Bright Data SERP API.

        Uses the /request endpoint to query Google/Bing for local business
        intelligence (e.g., "grocery stores Montgomery AL").
        Returns structured SERP results or simulated local results.
        """
        if not self.is_configured:
            return self._simulate_serp_response(query, engine, location, num_results)

        try:
            encoded_q = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_q}&hl=en&gl=us&num={num_results}"
            if engine == "bing":
                search_url = f"https://www.bing.com/search?q={encoded_q}"

            async with httpx.AsyncClient(timeout=45) as client:
                payload = {
                    "zone": self.serp_zone,
                    "url": search_url,
                    "format": "raw",
                }
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                }
                response = await client.post(
                    f"{self.base_url}/request",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                raw = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"raw_html": response.text[:5000]}
                return self._parse_serp_response(raw, query, engine, location)
        except Exception as e:
            logger.error("Bright Data SERP search failed: %s", e)
            simulated = self._simulate_serp_response(query, engine, location, num_results)
            simulated["error"] = str(e)
            simulated["source"] = "brightdata_serp_simulated_after_error"
            return simulated

    def _parse_serp_response(self, data: dict, query: str, engine: str, location: str) -> dict:
        """Parse Bright Data SERP API response."""
        # If structured JSON with organic results
        organic = data.get("organic", data.get("results", []))
        if isinstance(organic, list) and organic:
            results = []
            for item in organic[:10]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", item.get("url", "")),
                    "description": item.get("description", item.get("snippet", "")),
                    "position": item.get("global_rank", item.get("position", 0)),
                })
            return {
                "query": query,
                "engine": engine,
                "location": location,
                "result_count": len(results),
                "results": results,
                "source": "brightdata_serp",
                "is_live": True,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        # Fallback: raw HTML was returned
        return {
            "query": query,
            "engine": engine,
            "location": location,
            "result_count": 0,
            "results": [],
            "raw_preview": str(data)[:500],
            "source": "brightdata_serp",
            "is_live": True,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    def _simulate_serp_response(
        self, query: str, engine: str, location: str, num_results: int
    ) -> dict:
        """Generate deterministic simulated SERP results for demo mode."""
        rng = Random(self._seed_str(f"serp:{query}:{engine}"))
        categories = [
            ("Local Business Directory", "yellowpages.com"),
            ("Yelp Reviews", "yelp.com"),
            ("Google Maps", "google.com/maps"),
            ("Chamber of Commerce", "montgomerychamber.com"),
            ("City of Montgomery", "montgomeryal.gov"),
            ("Alabama Media Group", "al.com"),
            ("Better Business Bureau", "bbb.org"),
            ("TripAdvisor", "tripadvisor.com"),
        ]
        results = []
        for i in range(min(num_results, len(categories))):
            title_base, domain = categories[i]
            results.append({
                "title": f"{title_base} — {query} in Montgomery, AL",
                "url": f"https://www.{domain}/montgomery-al/{quote_plus(query.lower())}",
                "description": f"Find the best {query.lower()} options in Montgomery, Alabama. "
                               f"Ratings, reviews, and local insights for {location}.",
                "position": i + 1,
            })
        return {
            "query": query,
            "engine": engine,
            "location": location,
            "result_count": len(results),
            "results": results,
            "source": "brightdata_serp_simulated",
            "is_live": False,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    # ── Web Unlocker (scrape as markdown) ────────────────────────────────

    async def scrape_url(self, url: str) -> dict:
        """
        Scrape a public webpage via Bright Data's Web Unlocker API.

        Returns clean markdown content suitable for AI/LLM consumption.
        Handles anti-bot protection, CAPTCHAs, and dynamic rendering automatically.
        """
        if not self.is_configured:
            return self._simulate_scrape_response(url)

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                payload = {
                    "zone": self.unlocker_zone,
                    "url": url,
                    "format": "raw",
                    "data_format": "markdown",
                }
                headers = {
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json",
                }
                response = await client.post(
                    f"{self.base_url}/request",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                content = response.text
                # Truncate to reasonable size for LLM context
                if len(content) > 8000:
                    content = content[:8000] + "\n\n... (truncated)"
                return {
                    "url": url,
                    "content": content,
                    "content_length": len(response.text),
                    "source": "brightdata_unlocker",
                    "is_live": True,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as e:
            logger.error("Bright Data scrape failed for %s: %s", url, e)
            simulated = self._simulate_scrape_response(url)
            simulated["error"] = str(e)
            simulated["source"] = "brightdata_unlocker_simulated_after_error"
            return simulated

    def _simulate_scrape_response(self, url: str) -> dict:
        """Generate simulated scrape content for demo mode."""
        # Extract domain for realistic simulation
        domain_match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        domain = domain_match.group(1) if domain_match else "example.com"
        content = (
            f"# Content from {domain}\n\n"
            f"This is simulated content from Bright Data's Web Unlocker API.\n\n"
            f"**URL**: {url}\n\n"
            f"In live mode, this would contain the full page content scraped "
            f"through Bright Data's proxy infrastructure with automatic:\n"
            f"- CAPTCHA solving\n"
            f"- IP rotation\n"
            f"- Browser fingerprint management\n"
            f"- Rate limit handling\n\n"
            f"The content is returned as clean markdown, ready for LLM consumption.\n"
        )
        return {
            "url": url,
            "content": content,
            "content_length": len(content),
            "source": "brightdata_unlocker_simulated",
            "is_live": False,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    # ── Bright Data product capabilities summary ────────────────────────

    def get_capabilities(self) -> dict:
        """Return summary of all Bright Data products integrated."""
        return {
            "products": [
                {
                    "name": "Web Scraper (Datasets API)",
                    "description": "Google Maps POI and review data collection",
                    "endpoint": "/datasets/v3/trigger",
                    "status": "active" if self.is_configured else "simulated",
                    "methods": ["fetch_pois_near", "fetch_reviews_near", "fetch_activity_signals"],
                },
                {
                    "name": "SERP API",
                    "description": "Search engine results for local business intelligence",
                    "endpoint": "/request (SERP zone)",
                    "status": "active" if self.is_configured else "simulated",
                    "methods": ["search_serp"],
                },
                {
                    "name": "Web Unlocker",
                    "description": "Scrape any public webpage as clean markdown",
                    "endpoint": "/request (Unlocker zone)",
                    "status": "active" if self.is_configured else "simulated",
                    "methods": ["scrape_url"],
                },
                {
                    "name": "MCP Server",
                    "description": "AI agent web data access via Model Context Protocol",
                    "endpoint": "mcp.brightdata.com/sse",
                    "status": "documented",
                    "methods": ["search_engine", "scrape_as_markdown", "web_data_google_maps_reviews"],
                },
            ],
            "configured": self.is_configured,
            "mode": "live" if self.is_configured else "simulated",
        }

    # ── Helpers ──────────────────────────────────────────────────────────

    def _seed(self, lat: float, lng: float, suffix: str) -> int:
        key = f"{lat:.5f}:{lng:.5f}:{suffix}".encode("utf-8")
        digest = hashlib.sha256(key).hexdigest()[:12]
        return int(digest, 16)

    def _seed_str(self, suffix: str) -> int:
        """Seed from an arbitrary string (no coordinates)."""
        digest = hashlib.sha256(suffix.encode("utf-8")).hexdigest()[:12]
        return int(digest, 16)

    def _simulate_poi_response(self, lat: float, lng: float, category: str) -> dict:
        rng = Random(self._seed(lat, lng, f"poi:{category}"))
        total_count = rng.randint(4, 28)
        competitor_count = max(1, int(total_count * rng.uniform(0.25, 0.55)))
        return {
            "total_count": total_count,
            "competitor_count": competitor_count,
            "category": category,
            "source": "brightdata_simulated",
            "pois": [],
        }

    def _simulate_review_response(
        self,
        lat: float,
        lng: float,
        business_type: str,
    ) -> dict:
        rng = Random(self._seed(lat, lng, f"reviews:{business_type}"))
        avg_rating = round(rng.uniform(3.2, 4.7), 2)
        total_reviews = rng.randint(18, 480)
        return {
            "avg_rating": avg_rating,
            "total_reviews": total_reviews,
            "business_type": business_type,
            "source": "brightdata_simulated",
        }


# Singleton instance
_client: Optional[BrightDataClient] = None


def get_brightdata_client() -> BrightDataClient:
    global _client
    if _client is None:
        _client = BrightDataClient(strict=False)
    return _client
