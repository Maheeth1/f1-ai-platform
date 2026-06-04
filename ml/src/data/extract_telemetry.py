import pandas as pd
import numpy as np
from typing import Dict, List

def calculate_lap_telemetry(lap) -> Dict:
    """
    Extracts telemetry for a single lap and computes aggregated features.
    """
    # Return empty dict if telemetry is missing (e.g., incomplete lap)
    try:
        telemetry = lap.get_telemetry()
        if telemetry.empty:
            return {}
    except Exception:
        return {}

    # Average and Max/Min Speed
    speed = telemetry['Speed']
    avg_speed = speed.mean()
    max_speed = speed.max()
    min_speed = speed.min()

    # Throttle
    throttle = telemetry['Throttle']
    avg_throttle = throttle.mean()
    max_throttle = throttle.max()

    # Brake Percentage
    brake = telemetry['Brake']
    # FastF1 boolean arrays or 0-100 integers depending on the season
    if brake.dtype == bool:
        brake_percentage = brake.mean() * 100
    else:
        # Sometimes brake is mapped 0-100
        brake_percentage = (brake > 0).mean() * 100

    # DRS Usage Percentage
    drs = telemetry['DRS']
    # DRS typically >= 10 indicates DRS is open
    drs_percentage = (drs >= 10).mean() * 100

    # RPM
    rpm = telemetry['RPM']
    avg_rpm = rpm.mean()
    max_rpm = rpm.max()

    # Gear
    gear = telemetry['nGear']
    # Filter out anomalous 0 gears if present
    valid_gears = gear[gear > 0]
    avg_gear = valid_gears.mean() if not valid_gears.empty else np.nan

    # Cornering Speed Estimate (approximate by looking at min speeds during braking)
    # A simple estimate is the 10th percentile of speed
    cornering_speed = np.percentile(speed, 10) if not speed.empty else np.nan

    return {
        'AvgSpeed': avg_speed,
        'MaxSpeed': max_speed,
        'MinSpeed': min_speed,
        'AvgThrottle': avg_throttle,
        'MaxThrottle': max_throttle,
        'BrakePercentage': brake_percentage,
        'DRSPercentage': drs_percentage,
        'AvgRPM': avg_rpm,
        'MaxRPM': max_rpm,
        'AvgGear': avg_gear,
        'CorneringSpeed': cornering_speed
    }

def extract_session_telemetry(laps_df) -> pd.DataFrame:
    """
    Iterates through all laps in a session and extracts aggregated telemetry.
    Returns a DataFrame of telemetry features indexed to match the laps.
    """
    telemetry_records = []
    
    # Iterate using FastF1 lap objects
    for _, lap in laps_df.iterlaps():
        # FastF1 `iterlaps()` yields (index, Lap object)
        record = calculate_lap_telemetry(lap)
        telemetry_records.append(record)
        
    return pd.DataFrame(telemetry_records, index=laps_df.index)
