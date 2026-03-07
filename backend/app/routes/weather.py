"""
Weather routes for Montgomery, AL.

Uses Open-Meteo API — free, no API key required.
Weather data enhances site selection (foot traffic prediction,
construction scheduling, economic impact analysis).
"""

from fastapi import APIRouter

from app.services.weather_service import fetch_current_weather, fetch_weather_forecast

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/current")
async def get_current_weather():
    """Get current weather conditions for Montgomery, AL.

    Returns temperature, humidity, wind, precipitation.
    Weather affects foot traffic patterns and construction activity.
    """
    return await fetch_current_weather()


@router.get("/forecast")
async def get_weather_forecast():
    """Get 7-day weather forecast for Montgomery, AL.

    Useful for planning site visits, predicting foot traffic changes,
    and scheduling construction permits.
    """
    return await fetch_weather_forecast()
