from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cities_db = [
    {"id": 1, "name": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278},
    {"id": 2, "name": "New York", "country": "US", "lat": 40.7128, "lon": -74.0060},
    {"id": 3, "name": "Tokyo", "country": "JP", "lat": 35.6762, "lon": 139.6503},
]

weather_db = {}
favorites_db = []
unit_pref = "C"

class City(BaseModel):
    id: int
    name: str
    country: str
    lat: float
    lon: float

class Weather(BaseModel):
    city_id: int
    temperature: float
    conditions: str
    humidity: int
    wind_speed: float
    icon: str
    unit: str
    timestamp: datetime

class FavoriteOut(BaseModel):
    id: int
    user_id: int
    city_id: int
    city_name: str
    country: str
    created_at: datetime

class UnitToggle(BaseModel):
    unit: str

@app.get("/api/cities/search")
async def search_cities(q: str) -> List[City]:
    return [city for city in cities_db if q.lower() in city["name"].lower()]

@app.get("/api/weather/current")
async def get_current_weather(city_id: int) -> Weather:
    city = next((c for c in cities_db if c["id"] == city_id), None)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    if city_id not in weather_db:
        temp = round(random.uniform(5, 30), 1)
        weather_db[city_id] = {
            "city_id": city_id,
            "temperature": temp,
            "conditions": random.choice(["Sunny", "Cloudy", "Rainy", "Snowy"]),
            "humidity": random.randint(30, 90),
            "wind_speed": round(random.uniform(0, 15), 1),
            "icon": random.choice(["☀️", "☁️", "🌧️", "❄️"]),
            "unit": unit_pref,
            "timestamp": datetime.now()
        }
    return weather_db[city_id]

@app.get("/api/weather/forecast")
async def get_forecast(city_id: int) -> List[Weather]:
    city = next((c for c in cities_db if c["id"] == city_id), None)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    forecast = []
    for i in range(5):
        day = datetime.now() + timedelta(days=i)
        forecast.append({
            "city_id": city_id,
            "temperature": round(random.uniform(5, 30), 1),
            "conditions": random.choice(["Sunny", "Cloudy", "Rainy", "Snowy"]),
            "humidity": random.randint(30, 90),
            "wind_speed": round(random.uniform(0, 15), 1),
            "icon": random.choice(["☀️", "☁️", "🌧️", "❄️"]),
            "unit": unit_pref,
            "timestamp": day
        })
    return forecast

@app.post("/api/favorites")
async def add_favorite(city_id: int, user_id: int = 1):
    city = next((c for c in cities_db if c["id"] == city_id), None)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    fav_id = max([f["id"] for f in favorites_db], default=0) + 1
    favorite = {"id": fav_id, "user_id": user_id, "city_id": city_id, "created_at": datetime.now()}
    favorites_db.append(favorite)
    return favorite

@app.get("/api/favorites")
async def get_favorites(user_id: int = 1) -> List[FavoriteOut]:
    result = []
    for fav in favorites_db:
        if fav["user_id"] == user_id:
            city = next((c for c in cities_db if c["id"] == fav["city_id"]), None)
            if city:
                result.append({
                    "id": fav["id"],
                    "user_id": fav["user_id"],
                    "city_id": fav["city_id"],
                    "city_name": city["name"],
                    "country": city["country"],
                    "created_at": fav["created_at"]
                })
    return result

@app.delete("/api/favorites/{fav_id}")
async def delete_favorite(fav_id: int):
    global favorites_db
    favorites_db = [f for f in favorites_db if f["id"] != fav_id]
    return {"message": "Favorite deleted"}

@app.put("/api/weather/unit")
async def toggle_unit(toggle: UnitToggle):
    global unit_pref
    unit_pref = toggle.unit if toggle.unit in ["C", "F"] else "C"
    return {"unit": unit_pref}
