import pandas as pd
import numpy as np
from src.utils.logger import get_logger

logger = get_logger(__name__)

def generate_rolling_pace(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates rolling lap times (Previous Lap, Avg Last 3/5/10 Laps).
    Assumes dataframe is sorted by Year, EventName, SessionType, Driver, and LapNumber.
    """
    logger.info("Generating Rolling Pace Features...")
    # Convert LapTime timedelta to seconds if not already
    if pd.api.types.is_timedelta64_dtype(df['LapTime']):
        df['LapTimeSeconds'] = df['LapTime'].dt.total_seconds()
    elif 'LapTimeSeconds' not in df.columns:
        # Fallback if LapTime is a string or already float
        df['LapTimeSeconds'] = pd.to_numeric(df['LapTime'], errors='coerce')
        
    group = df.groupby(['Year', 'EventName', 'SessionType', 'Driver'])
    
    df['PrevLapTime'] = group['LapTimeSeconds'].shift(1)
    df['AvgLast3Laps'] = group['LapTimeSeconds'].transform(lambda x: x.rolling(3, min_periods=1).mean().shift(1))
    df['AvgLast5Laps'] = group['LapTimeSeconds'].transform(lambda x: x.rolling(5, min_periods=1).mean().shift(1))
    df['AvgLast10Laps'] = group['LapTimeSeconds'].transform(lambda x: x.rolling(10, min_periods=1).mean().shift(1))
    
    # Driver Consistency (Rolling Std Dev)
    df['DriverConsistency3Laps'] = group['LapTimeSeconds'].transform(lambda x: x.rolling(3, min_periods=2).std().shift(1))
    df['DriverConsistency5Laps'] = group['LapTimeSeconds'].transform(lambda x: x.rolling(5, min_periods=2).std().shift(1))
    
    return df

def generate_tire_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates Tire Age, Tire Degradation Index.
    """
    logger.info("Generating Tire Features...")
    # FastF1 typically provides TyreLife. If not, we estimate it from Stint and LapNumber.
    if 'TyreLife' not in df.columns:
        group = df.groupby(['Year', 'EventName', 'SessionType', 'Driver', 'Stint'])
        df['TyreLife'] = group.cumcount() + 1
        
    # Fix Target Leakage: use rolling min of PrevLapTime for StintBestLap
    stint_group = df.groupby(['Year', 'EventName', 'SessionType', 'Driver', 'Stint'])
    
    if 'PrevLapTime' in df.columns:
        df['StintBestLapSoFar'] = stint_group['PrevLapTime'].cummin()
        df['TireDegradationIndex'] = df['PrevLapTime'] - df['StintBestLapSoFar']
        df.drop(columns=['StintBestLapSoFar'], inplace=True, errors='ignore')
    else:
        df['TireDegradationIndex'] = np.nan
        
    # Note: StintMaxLife and StintProgress removed due to future data leakage
    
    return df

def generate_race_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates Position Change based on historical position to avoid leakage.
    """
    logger.info("Generating Race Features...")
    
    if 'Position' in df.columns:
        driver_group = df.groupby(['Year', 'EventName', 'SessionType', 'Driver'])
        # Shift Position to prevent target leakage (Position is known at end of lap)
        df['PrevPosition'] = driver_group['Position'].shift(1)
        df['StartingPosition'] = driver_group['Position'].transform('first')
        df['PositionChange'] = df['StartingPosition'] - df['PrevPosition']
    else:
        df['PositionChange'] = np.nan
        
    return df

def generate_track_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds Track-specific flags (Street, Permanent, High Speed, High Downforce).
    """
    logger.info("Generating Track Features...")
    
    street_circuits = ['Monaco', 'Baku', 'Singapore', 'Las Vegas', 'Jeddah', 'Miami', 'Marina Bay']
    high_speed_circuits = ['Monza', 'Jeddah', 'Silverstone', 'Spa-Francorchamps', 'Las Vegas']
    high_downforce_circuits = ['Monaco', 'Singapore', 'Hungaroring', 'Zandvoort']
    
    df['IsStreetCircuit'] = df['Circuit'].apply(lambda x: 1 if any(sc in str(x) for sc in street_circuits) else 0)
    df['IsHighSpeed'] = df['Circuit'].apply(lambda x: 1 if any(hs in str(x) for hs in high_speed_circuits) else 0)
    df['IsHighDownforce'] = df['Circuit'].apply(lambda x: 1 if any(hd in str(x) for hd in high_downforce_circuits) else 0)
    df['IsPermanentCircuit'] = 1 - df['IsStreetCircuit']
    
    return df

def generate_historical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Shifts telemetry and sector features by 1 lap to prevent target leakage.
    These features represent the performance of the *previous* lap.
    """
    logger.info("Generating Historical Telemetry/Sector Features...")
    
    cols_to_shift = [
        'Sector1Time', 'Sector2Time', 'Sector3Time',
        'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST', 
        'AvgSpeed', 'MaxSpeed', 'MinSpeed', 'AvgThrottle', 'MaxThrottle', 
        'BrakePercentage', 'DRSPercentage', 'AvgRPM', 'MaxRPM', 'AvgGear', 'CorneringSpeed'
    ]
    
    group = df.groupby(['Year', 'EventName', 'SessionType', 'Driver'])
    
    for col in cols_to_shift:
        if col in df.columns:
            # Shift the feature and create a 'Prev' version
            df[f'Prev{col}'] = group[col].shift(1)
            
            # If the column is a timedelta, convert the shifted version to seconds
            if pd.api.types.is_timedelta64_dtype(df[f'Prev{col}']):
                df[f'Prev{col}Seconds'] = df[f'Prev{col}'].dt.total_seconds()
                
    return df

def generate_advanced_race_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates advanced race features like Fuel Effect and Track Evolution.
    """
    logger.info("Generating Advanced Race Features...")
    
    # Fuel Effect: Assumption that burning fuel saves ~0.06 seconds per lap
    if 'LapNumber' in df.columns:
        df['FuelEffect'] = df['LapNumber'] * 0.06
    else:
        df['FuelEffect'] = np.nan
        
    # Track Evolution: The minimum PrevLapTime recorded in the session up to the current point
    if 'PrevLapTime' in df.columns and 'LapNumber' in df.columns:
        # Sort chronologically across all drivers to compute session-wide evolution
        df = df.sort_values(by=['Year', 'EventName', 'SessionType', 'LapNumber'])
        session_group = df.groupby(['Year', 'EventName', 'SessionType'])
        df['TrackEvolution'] = session_group['PrevLapTime'].transform(lambda x: x.expanding().min())
        
        # Re-sort back to driver-focused ordering for consistency
        df = df.sort_values(by=['Year', 'EventName', 'SessionType', 'Driver', 'LapNumber'])
    else:
        df['TrackEvolution'] = np.nan
        
    return df

def run_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs the full feature engineering pipeline sequentially.
    """
    # Sort data chronologically to ensure rolling features work correctly
    df = df.sort_values(by=['Year', 'EventName', 'SessionType', 'Driver', 'LapNumber'])
    
    df = generate_rolling_pace(df)
    df = generate_tire_features(df)
    df = generate_race_features(df)
    df = generate_track_features(df)
    df = generate_historical_features(df)
    df = generate_advanced_race_features(df)
    
    logger.info(f"Feature engineering complete. Total features: {len(df.columns)}")
    return df
