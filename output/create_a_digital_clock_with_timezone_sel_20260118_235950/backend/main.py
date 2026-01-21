from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
from typing import Dict, List
import tzlocal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TIMEZONES = [
    {"label": "UTC-5: New York", "value": "America/New_York"},
    {"label": "UTC+0: London", "value": "Europe/London"},
    {"label": "UTC+1: Berlin", "value": "Europe/Berlin"},
    {"label": "UTC+8: Beijing", "value": "Asia/Shanghai"},
    {"label": "UTC+9: Tokyo", "value": "Asia/Tokyo"},
]

user_settings: Dict[str, Dict] = {}
local_tz = tzlocal.get_localzone_name()

def get_current_time(timezone: str, hour_format: str) -> Dict:
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        if hour_format == "12":
            hour = now.strftime("%I")
            am_pm = now.strftime("%p")
            time_str = f"{hour}:{now.strftime('%M:%S')} {am_pm}"
        else:
            time_str = now.strftime("%H:%M:%S")
        return {
            "hour": int(now.strftime("%H")),
            "minute": int(now.strftime("%M")),
            "second": int(now.strftime("%S")),
            "formatted": time_str,
            "timezone": timezone,
        }
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid timezone")

@app.get("/api/current-time")
def get_time(user_id: str = "default", timezone: str = None, hour_format: str = None):
    settings = user_settings.get(user_id, {"timezone": local_tz, "hour_format": "24"})
    tz = timezone or settings.get("timezone", local_tz)
    fmt = hour_format or settings.get("hour_format", "24")
    return get_current_time(tz, fmt)

@app.get("/api/timezones")
def list_timezones() -> List[Dict]:
    return TIMEZONES

@app.get("/api/user-settings")
def get_settings(user_id: str = "default"):
    return user_settings.get(user_id, {"timezone": local_tz, "hour_format": "24"})

@app.post("/api/user-settings")
def update_settings(user_id: str = "default", timezone: str = None, hour_format: str = None):
    if user_id not in user_settings:
        user_settings[user_id] = {"timezone": local_tz, "hour_format": "24"}
    if timezone:
        user_settings[user_id]["timezone"] = timezone
    if hour_format:
        user_settings[user_id]["hour_format"] = hour_format
    return user_settings[user_id]
