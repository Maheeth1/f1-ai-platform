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
    Calculates Tire Age, Tire Degradation Index, and Stint Progress.
    """
    logger.info("Generating Tire Features...")
    # FastF1 typically provides TyreLife. If not, we estimate it from Stint and LapNumber.
    if 'TyreLife' not in df.columns:
        group = df.groupby(['Year', 'EventName', 'SessionType', 'Driver', 'Stint'])
        df['TyreLife'] = group.cumcount() + 1
        
    # Tire Degradation Index = (Current Lap Time - Stint Best Lap Time)
    stint_group = df.groupby(['Year', 'EventName', 'SessionType', 'Driver', 'Stint'])
    df['StintBestLap'] = stint_group['LapTimeSeconds'].transform('min')
    df['TireDegradationIndex'] = df['LapTimeSeconds'] - df['StintBestLap']
    
    # Stint Progress = TyreLife / Max TyreLife in that stint
    df['StintMaxLife'] = stint_group['TyreLife'].transform('max')
    df['StintProgress'] = df['TyreLife'] / df['StintMaxLife']
    
    # Drop intermediate columns
    df.drop(columns=['StintBestLap', 'StintMaxLife'], inplace=True, errors='ignore')
    return df

def generate_race_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates Gap To Leader, Position Change, and Current Race Position.
    """
    logger.info("Generating Race Features...")
    
    if 'Position' in df.columns:
        # Position change since Lap 1
        driver_group = df.groupby(['Year', 'EventName', 'SessionType', 'Driver'])
        df['StartingPosition'] = driver_group['Position'].transform('first')
        df['PositionChange'] = df['StartingPosition'] - df['Position']
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
    
    logger.info(f"Feature engineering complete. Total features: {len(df.columns)}")
    return df
