import fastf1
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
from app.api.middleware.cache import cached

router = APIRouter()

# Enable cache for fastf1
fastf1.Cache.enable_cache('data/cache')

@router.get("/standings")
@cached(ttl=3600)
def get_standings():
    """
    Returns championship standings.
    Using mocked data here for prototype purposes to power the Dashboard UI, 
    but served from the backend.
    """
    return [
        {"name": "Max Verstappen", "points": 430, "wins": 19, "podiums": 21, "team": "Red Bull"},
        {"name": "Lando Norris", "points": 285, "wins": 2, "podiums": 11, "team": "McLaren"},
        {"name": "Charles Leclerc", "points": 250, "wins": 3, "podiums": 9, "team": "Ferrari"},
        {"name": "Lewis Hamilton", "points": 220, "wins": 1, "podiums": 6, "team": "Mercedes"},
        {"name": "Carlos Sainz", "points": 200, "wins": 2, "podiums": 7, "team": "Ferrari"}
    ]

@router.get("/track/{year}/{race_name}")
@cached(ttl=86400) # Cache for 24 hours
def get_track_telemetry(year: int, race_name: str, session_type: str = 'R'):
    """
    Fetches the track coordinates and base telemetry for a lap using FastF1.
    """
    try:
        session = fastf1.get_session(year, race_name, session_type)
        session.load(telemetry=True, weather=False, messages=False)
        
        # Get the fastest lap of the session to map the track
        if len(session.laps) == 0:
            raise ValueError("No fastest lap found")
        fastest_lap = session.laps.pick_fastest()
            
        telemetry = fastest_lap.get_telemetry()
        
        # Sample the data to reduce payload size (every 5th data point)
        sampled = telemetry.iloc[::5]
        
        segments = []
        for i, row in sampled.iterrows():
            segments.append({
                "x": float(row['X']) / 10 if not pd_is_null(row['X']) else 0, # Scale down
                "y": float(row['Y']) / 10 if not pd_is_null(row['Y']) else 0,
                "telemetry": {
                    "speed": float(row['Speed']) if not pd_is_null(row['Speed']) else 0,
                    "throttle": float(row['Throttle']) if not pd_is_null(row['Throttle']) else 0,
                    "brake": float(row['Brake']) if not pd_is_null(row['Brake']) else 0,
                    "gear": int(row['nGear']) if not pd_is_null(row['nGear']) else 0,
                    "rpm": int(row['RPM']) if not pd_is_null(row['RPM']) else 0
                }
            })
            
        return {"segments": segments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/telemetry/comparison")
@cached(ttl=86400)
def get_telemetry_comparison(
    year: int = Query(2023), 
    race_name: str = Query("Monaco"), 
    driver1: str = Query("VER"), 
    driver2: str = Query("NOR")
):
    """
    Fetches side-by-side telemetry trace comparison for two drivers using FastF1.
    """
    try:
        session = fastf1.get_session(year, race_name, 'R')
        session.load(telemetry=True, weather=False, messages=False)
        
        laps_d1 = session.laps.pick_driver(driver1)
        laps_d2 = session.laps.pick_driver(driver2)
        
        if len(laps_d1) == 0 or len(laps_d2) == 0:
            raise ValueError("Could not find fastest lap for one or both drivers")

        lap_d1 = laps_d1.pick_fastest()
        lap_d2 = laps_d2.pick_fastest()

        tel_d1 = lap_d1.get_telemetry()
        tel_d2 = lap_d2.get_telemetry()
        
        # In a real app we'd align the distance arrays. For now we will return 
        # sampled data arrays independently, or align them simply.
        # This is simplified.
        
        traces = []
        min_len = min(len(tel_d1), len(tel_d2))
        
        for i in range(0, min_len, 10): # Sample every 10th row
            traces.append({
                "distance": float(tel_d1['Distance'].iloc[i]),
                "verSpeed": float(tel_d1['Speed'].iloc[i]),
                "norSpeed": float(tel_d2['Speed'].iloc[i]),
                "verThrottle": float(tel_d1['Throttle'].iloc[i]),
                "norThrottle": float(tel_d2['Throttle'].iloc[i]),
                "delta": float(tel_d1['Time'].iloc[i].total_seconds() - tel_d2['Time'].iloc[i].total_seconds()) if hasattr(tel_d1['Time'].iloc[i], 'total_seconds') else 0
            })
            
        return {"traces": traces}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def pd_is_null(val):
    import pandas as pd
    return pd.isna(val)
