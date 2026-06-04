import os
import fastf1
import pandas as pd
from typing import List, Optional
import sys
from pathlib import Path

# Add the src directory to path to allow absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import TARGET_YEARS, FASTF1_CACHE_DIR, RAW_DATA_DIR
from src.utils.logger import get_logger

logger = get_logger(__name__)

def setup_fastf1():
    """Enable FastF1 cache to prevent redundant API calls."""
    fastf1.Cache.enable_cache(str(FASTF1_CACHE_DIR))
    logger.info(f"FastF1 cache enabled at: {FASTF1_CACHE_DIR}")

from src.data.extract_weather import extract_weather_data
from src.data.extract_telemetry import extract_session_telemetry

def get_session_data(year: int, event_name: str, session_identifier: str) -> Optional[tuple]:
    """
    Downloads and extracts basic lap, weather, and telemetry data.
    Returns (laps_df, weather_df, telemetry_df)
    """
    try:
        session = fastf1.get_session(year, event_name, session_identifier)
        # Load session WITH weather and telemetry
        session.load(telemetry=True, weather=True, messages=False)
        
        if session.laps.empty:
            logger.warning(f"No laps found for {year} {event_name} - {session_identifier}")
            return None
            
        laps = session.laps.copy()
        
        # Extract basic Race Information
        laps['Year'] = year
        laps['EventName'] = session.event['EventName']
        laps['Country'] = session.event['Country']
        laps['Circuit'] = session.event.get('Location', 'Unknown')
        laps['RoundNumber'] = session.event['RoundNumber']
        laps['SessionType'] = session.name
        
        if 'Driver' not in laps.columns:
            logger.warning(f"No Driver column in {year} {event_name}")

        # Phase 2: Weather extraction
        weather_df = extract_weather_data(session.laps)
        
        # Phase 3: Telemetry extraction (slow step)
        logger.info(f"Extracting telemetry for {year} {event_name} (this may take a while...)")
        telemetry_df = extract_session_telemetry(session.laps)
            
        return laps, weather_df, telemetry_df

    except Exception as e:
        logger.error(f"Failed to fetch {year} {event_name} {session_identifier}: {str(e)}")
        return None

import concurrent.futures

def process_session(year: int, event_name: str, session_id: str, laps_dir, weather_dir, telemetry_dir):
    safe_event_name = event_name.replace(" ", "_").replace("/", "")
    
    output_laps = laps_dir / f"{year}_{safe_event_name}_{session_id}.csv"
    output_weather = weather_dir / f"{year}_{safe_event_name}_{session_id}.csv"
    output_telemetry = telemetry_dir / f"{year}_{safe_event_name}_{session_id}.csv"
    
    if output_laps.exists() and output_weather.exists() and output_telemetry.exists():
        logger.info(f"Skipping {year} {event_name} {session_id} - already downloaded.")
        return
        
    result = get_session_data(year, event_name, session_id)
    if result:
        laps, weather, telemetry = result
        
        if not laps.empty:
            laps.to_csv(output_laps, index=False)
        if not weather.empty:
            weather.to_csv(output_weather, index=False)
        if not telemetry.empty:
            telemetry.to_csv(output_telemetry, index=False)
            
        logger.info(f"Saved {len(laps)} laps for {year} {event_name} {session_id}")
    else:
        logger.info(f"No data saved for {year} {event_name} {session_id}")

def main():
    setup_fastf1()
    
    # Create sub-directories
    laps_dir = RAW_DATA_DIR / "laps"
    weather_dir = RAW_DATA_DIR / "weather"
    telemetry_dir = RAW_DATA_DIR / "telemetry"
    
    for d in [laps_dir, weather_dir, telemetry_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Collect all tasks
    tasks = []
    
    for year in TARGET_YEARS:
        logger.info(f"=== Fetching Schedule for Year {year} ===")
        try:
            events = fastf1.get_event_schedule(year)
        except Exception as e:
            logger.error(f"Failed to fetch schedule for {year}: {e}")
            continue
            
        for _, event in events.iterrows():
            event_name = event['EventName']
            if event_name == 'Pre-Season Testing':
                continue
                
            for session_id in ['Q', 'R']:
                tasks.append((year, event_name, session_id, laps_dir, weather_dir, telemetry_dir))
                
    logger.info(f"Total sessions to process: {len(tasks)}")
    
    # Run concurrently using ThreadPoolExecutor
    # max_workers=4 prevents overwhelming the API and getting rate limited
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_session, *task) for task in tasks]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                logger.error(f"A session processing task generated an exception: {exc}")

if __name__ == "__main__":
    main()
