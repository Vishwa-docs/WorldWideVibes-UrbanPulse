"""
Weather service for Montgomery, AL.

Uses the Open-Meteo API — free, no API key required.
Provides current conditions and 7-day forecast for site selection
and economic impact analysis (weather affects foot traffic, construction, etc.).
"""

import httpx
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Montgomery, AL coordinates
MONTGOMERY_LAT = 32.3668
MONTGOMERY_LNG = -86.3000

OPEN_METEO_CURRENT = "https://api.open-meteo.com/v1/forecast"


async def fetch_current_weather() -> dict:
    """Fetch current weather conditions for Montgomery, AL.

    Returns temperature, humidity, wind, precipitation, and weather description.
    Uses Open-Meteo API (free, no key required).
    """
    params = {
        "latitude": MONTGOMERY_LAT,
        "longitude": MONTGOMERY_LNG,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "precipitation,weather_code,wind_speed_10m,wind_direction_10m"
        ),
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "America/Chicago",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(OPEN_METEO_CURRENT, params=params)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current", {})
        return {
            "location": "Montgomery, AL",
            "temperature_f": current.get("temperature_2m"),
            "feels_like_f": current.get("apparent_temperature"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "precipitation_in": current.get("precipitation"),
            "wind_speed_mph": current.get("wind_speed_10m"),
            "wind_direction": current.get("wind_direction_10m"),
            "weather_code": current.get("weather_code"),
            "weather_description": _weather_code_to_text(current.get("weather_code", 0)),
            "source": "open_meteo",
            "is_live": True,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error("Weather fetch failed: %s", e)
        return _simulated_weather()


async def fetch_weather_forecast() -> dict:
    """Fetch 7-day weather forecast for Montgomery, AL.

    Useful for construction permit scheduling, event planning,
    and foot traffic predictions.
    """
    params = {
        "latitude": MONTGOMERY_LAT,
        "longitude": MONTGOMERY_LNG,
        "daily": (
            "temperature_2m_max,temperature_2m_min,precipitation_sum,"
            "weather_code,wind_speed_10m_max"
        ),
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "America/Chicago",
        "forecast_days": 7,
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(OPEN_METEO_CURRENT, params=params)
            resp.raise_for_status()
            data = resp.json()

        daily = data.get("daily", {})
        dates = daily.get("time", [])
        forecast_days = []
        for i, date in enumerate(dates):
            forecast_days.append({
                "date": date,
                "high_f": daily.get("temperature_2m_max", [None])[i] if i < len(daily.get("temperature_2m_max", [])) else None,
                "low_f": daily.get("temperature_2m_min", [None])[i] if i < len(daily.get("temperature_2m_min", [])) else None,
                "precipitation_in": daily.get("precipitation_sum", [0])[i] if i < len(daily.get("precipitation_sum", [])) else 0,
                "wind_max_mph": daily.get("wind_speed_10m_max", [0])[i] if i < len(daily.get("wind_speed_10m_max", [])) else 0,
                "weather_code": daily.get("weather_code", [0])[i] if i < len(daily.get("weather_code", [])) else 0,
                "weather_description": _weather_code_to_text(
                    daily.get("weather_code", [0])[i] if i < len(daily.get("weather_code", [])) else 0
                ),
            })

        return {
            "location": "Montgomery, AL",
            "forecast": forecast_days,
            "source": "open_meteo",
            "is_live": True,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error("Weather forecast failed: %s", e)
        return _simulated_forecast()


def _weather_code_to_text(code: int) -> str:
    """Convert WMO weather code to human-readable description."""
    codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, f"Weather code {code}")


def _simulated_weather() -> dict:
    """Deterministic fallback for demo mode."""
    return {
        "location": "Montgomery, AL",
        "temperature_f": 72,
        "feels_like_f": 74,
        "humidity_pct": 58,
        "precipitation_in": 0.0,
        "wind_speed_mph": 8.5,
        "wind_direction": 180,
        "weather_code": 2,
        "weather_description": "Partly cloudy",
        "source": "open_meteo_simulated",
        "is_live": False,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _simulated_forecast() -> dict:
    """Deterministic fallback forecast."""
    from datetime import timedelta

    today = datetime.now().date()
    days = []
    base_temps = [72, 74, 68, 71, 76, 73, 70]
    codes = [2, 1, 3, 61, 0, 1, 2]
    for i in range(7):
        dt = today + timedelta(days=i)
        days.append({
            "date": dt.isoformat(),
            "high_f": base_temps[i] + 8,
            "low_f": base_temps[i] - 12,
            "precipitation_in": 0.3 if codes[i] >= 51 else 0.0,
            "wind_max_mph": 10 + i,
            "weather_code": codes[i],
            "weather_description": _weather_code_to_text(codes[i]),
        })
    return {
        "location": "Montgomery, AL",
        "forecast": days,
        "source": "open_meteo_simulated",
        "is_live": False,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
