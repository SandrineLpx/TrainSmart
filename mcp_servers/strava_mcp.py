"""
Strava MCP Server for Train Smart.
Fetches recent activities via Strava API v3.
Handles OAuth2 token refresh automatically.

Setup: Run scripts/strava_auth.py first to get your tokens.
"""

import json
import os
import ssl
import time
import urllib.parse
import urllib.request

from fastmcp import FastMCP

# Fix SSL certificate issues on Windows
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()
    SSL_CONTEXT.check_hostname = False
    SSL_CONTEXT.verify_mode = ssl.CERT_NONE

mcp = FastMCP(name="strava")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "strava_config.json")
_CACHE_TTL = 21600  # 6 hours
_config_cache = None  # in-process config cache
_activity_cache = {}  # key: days_back -> {"ts": float, "data": str}


def _load_config():
    global _config_cache
    if _config_cache is not None:
        return _config_cache.copy()
    with open(CONFIG_PATH, encoding="utf-8") as f:
        _config_cache = json.load(f)
        return _config_cache.copy()


def _save_config(config):
    global _config_cache
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    _config_cache = config.copy()


def _refresh_token_if_needed(config):
    """Refresh Strava access token if expired."""
    if time.time() >= config.get("expires_at", 0):
        data = urllib.parse.urlencode({
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "grant_type": "refresh_token",
            "refresh_token": config["refresh_token"],
        }).encode()
        req = urllib.request.Request(
            "https://www.strava.com/oauth/token", data=data, method="POST"
        )
        with urllib.request.urlopen(req, timeout=10, context=SSL_CONTEXT) as resp:
            token_data = json.loads(resp.read())
        config["access_token"] = token_data["access_token"]
        config["refresh_token"] = token_data["refresh_token"]
        config["expires_at"] = token_data["expires_at"]
        _save_config(config)
    return config


def _is_configured(config):
    """Check if Strava credentials have been set up."""
    return (
        config.get("access_token", "") != ""
        and config.get("client_id", "") not in ("", "YOUR_CLIENT_ID")
    )


@mcp.tool
def get_activities(days_back: int = 7) -> str:
    """Get recent Strava activities (bike, run, ski, walk, etc.) for the past
    N days. Returns activity name, type, distance (miles), duration (minutes),
    and date for each activity."""
    cached = _activity_cache.get(days_back)
    if cached and time.time() - cached["ts"] < _CACHE_TTL:
        return cached["data"]

    config = _load_config()

    if not _is_configured(config):
        return json.dumps({
            "status": "not_configured",
            "message": (
                "Strava is not connected yet. "
                "To connect, run: python scripts/strava_auth.py "
                "(you will need a free Strava API app from https://www.strava.com/settings/api). "
                "This is optional — you can still use the system by entering cardio manually."
            ),
        })

    config = _refresh_token_if_needed(config)

    after_timestamp = int(time.time()) - (days_back * 86400)
    url = (
        f"https://www.strava.com/api/v3/athlete/activities"
        f"?after={after_timestamp}&per_page=30"
    )
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {config['access_token']}")

    with urllib.request.urlopen(req, timeout=10, context=SSL_CONTEXT) as resp:
        activities = json.loads(resp.read())

    result = []
    for act in activities:
        distance_m = act.get("distance", 0)
        moving_time_s = act.get("moving_time", 0)
        result.append({
            "name": act.get("name"),
            "type": act.get("type"),
            "sport_type": act.get("sport_type"),
            "distance_miles": round(distance_m / 1609.34, 1),
            "moving_time_minutes": round(moving_time_s / 60),
            "date": act.get("start_date_local", "")[:10],
            "start_time": act.get("start_date_local", ""),
        })

    response = json.dumps(result, indent=2)
    _activity_cache[days_back] = {"ts": time.time(), "data": response}
    return response


if __name__ == "__main__":
    mcp.run()
