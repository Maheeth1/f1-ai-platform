from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any
from app.schemas.prediction import PredictionRequest
from app.api.dependencies import get_current_user
from app.services.simulation.monte_carlo import MonteCarloSimulator
from app.services.simulation.strategy_simulator import StrategySimulator
from app.services.simulation.driver_comparison import DriverComparisonEngine

router = APIRouter(
    prefix="/simulation",
    tags=["Simulation Engines"]
)

@router.post("/monte-carlo", response_model=Dict[str, Any])
async def run_monte_carlo(
    request: PredictionRequest,
    iterations: int = Query(100, ge=10, le=1000)
):
    """Run a Monte Carlo race simulation for lap time distribution."""
    try:
        simulator = MonteCarloSimulator()
        result = simulator.run_simulation(request, iterations=iterations)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/strategy/optimal-pit", response_model=Dict[str, Any])
async def optimal_pit_strategy(
    request: PredictionRequest,
    total_laps: int = Query(50, ge=5, le=100)
):
    """Find the optimal pit stop lap for a given stint."""
    try:
        simulator = StrategySimulator()
        result = simulator.find_optimal_pitstop(request, total_laps=total_laps)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/driver-comparison", response_model=Dict[str, Any])
async def compare_drivers(
    request: PredictionRequest,
    driver_1: str = Query(..., description="First driver code, e.g., VER"),
    driver_2: str = Query(..., description="Second driver code, e.g., HAM")
):
    """Head-to-head comparison of two drivers under identical conditions."""
    try:
        engine = DriverComparisonEngine()
        result = engine.compare_drivers(request, driver_1=driver_1, driver_2=driver_2)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
