"""
Weather MCP Server for Train Smart.
Fetches forecast from Open-Meteo API (free, no API key needed).
Configured for Kirkland, WA 98034.
"""

import json
import os
import time
import urllib.request

from fastmcp import FastMCP

mcp = FastMCP(name="weather")

PREFS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "preferences.json")
_CACHE_TTL = 43200  # 12 hours
_cache = {}  # key: (lat, lon, days) -> {"ts": float, "data": str}


def _load_preferences():
    try:
        with open(PREFS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "latitude": 47.6769,
            "longitude": -122.2060,
            "outdoor_thresholds": {
                "max_precipitation_pct": 40,
                "min_temp_f": 40,
                "max_wind_mph": 25,
            },
        }


def _f_to_c(f):
    """Convert Fahrenheit to Celsius, rounded to 1 decimal."""
    return round((f - 32) * 5 / 9, 1)


@mcp.tool
def get_forecast(days: int = 7) -> str:
    """Get weather forecast for Kirkland, WA. Returns daily temp high/low (F),
    precipitation probability, wind speed, and whether each day is suitable
    for outdoor training (bike/run/ski)."""
    prefs = _load_preferences()
    lat = prefs.get("latitude", 47.6769)
    lon = prefs.get("longitude", -122.2060)
    thresholds = prefs.get("outdoor_thresholds", {})

    cache_key = (lat, lon, days)
    cached = _cache.get(cache_key)
    if cached and time.time() - cached["ts"] < _CACHE_TTL:
        return cached["data"]

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,"
        f"precipitation_probability_max,wind_speed_10m_max"
        f"&temperature_unit=fahrenheit&wind_speed_unit=mph"
        f"&timezone=America%2FLos_Angeles&forecast_days={days}"
    )

    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())

    daily = data["daily"]
    max_rain = thresholds.get("max_precipitation_pct", 40)
    min_temp = thresholds.get("min_temp_f", 40)
    max_wind = thresholds.get("max_wind_mph", 25)

    result = []
    for i in range(len(daily["time"])):
        rain_pct = daily["precipitation_probability_max"][i]
        temp_high_f = daily["temperature_2m_max"][i]
        temp_low_f = daily["temperature_2m_min"][i]
        wind = daily["wind_speed_10m_max"][i]

        result.append({
            "date": daily["time"][i],
            "temp_high_c": _f_to_c(temp_high_f),
            "temp_high_f": temp_high_f,
            "temp_low_c": _f_to_c(temp_low_f),
            "temp_low_f": temp_low_f,
            "precipitation_probability_pct": rain_pct,
            "wind_max_mph": wind,
            "outdoor_suitable": (
                rain_pct < max_rain
                and temp_high_f > min_temp
                and wind < max_wind
            ),
        })

    response = json.dumps(result, indent=2)
    _cache[cache_key] = {"ts": time.time(), "data": response}
    return response


if __name__ == "__main__":
    mcp.run()
