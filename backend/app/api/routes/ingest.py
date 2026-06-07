from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.data_ingestion import ingest_session_data

router = APIRouter()

@router.post("/session/{year}/{race_name}")
async def trigger_ingestion(
    year: int, 
    race_name: str, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger background ingestion of FastF1 data for a specific race.
    """
    background_tasks.add_task(ingest_session_data, db, year, race_name)
    return {"message": f"Data ingestion for {year} {race_name} started in the background."}
