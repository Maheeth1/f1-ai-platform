import fastf1
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Driver, Team, Race, Telemetry
import pandas as pd
from app.core.logger import logger

# Enable cache for fastf1
fastf1.Cache.enable_cache('data/cache')

async def ingest_session_data(db: AsyncSession, year: int, race_name: str, session_type: str = 'R'):
    try:
        logger.info(f"Loading FastF1 data for {year} {race_name} {session_type}...")
        session = fastf1.get_session(year, race_name, session_type)
        session.load()
        
        # 1. Ingest Race
        race_query = await db.execute(select(Race).filter_by(season=year, name=session.event['EventName']))
        race = race_query.scalar_one_or_none()
        if not race:
            race = Race(
                season=year,
                round=session.event['RoundNumber'],
                name=session.event['EventName'],
                date=session.date,
                circuit_id=session.event['Location']
            )
            db.add(race)
            await db.commit()
            await db.refresh(race)
        
        # 2. Ingest Drivers & Teams
        for driver_id in session.drivers:
            driver_info = session.get_driver(driver_id)
            
            # Team
            team_query = await db.execute(select(Team).filter_by(name=driver_info['TeamName']))
            team = team_query.scalar_one_or_none()
            if not team:
                team = Team(
                    constructor_id=driver_info['TeamId'],
                    name=driver_info['TeamName'],
                    nationality="" # FastF1 doesn't provide team nationality directly
                )
                db.add(team)
                await db.commit()
                await db.refresh(team)
            
            # Driver
            drv_query = await db.execute(select(Driver).filter_by(code=driver_info['Abbreviation']))
            driver = drv_query.scalar_one_or_none()
            if not driver:
                driver = Driver(
                    driver_id=driver_info['DriverId'],
                    code=driver_info['Abbreviation'],
                    number=driver_info['DriverNumber'],
                    first_name=driver_info['FirstName'],
                    last_name=driver_info['LastName'],
                    nationality=driver_info['CountryCode']
                )
                db.add(driver)
                await db.commit()
                await db.refresh(driver)
        
        logger.info(f"Successfully ingested metadata for {year} {race_name}")
        return True
    except Exception as e:
        logger.error(f"Error ingesting session data: {e}")
        return False
