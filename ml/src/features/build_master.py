import pandas as pd
from pathlib import Path
import glob
import sys

# Add the src directory to path to allow absolute imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utils.logger import get_logger
from src.features.feature_engineering import run_feature_engineering

logger = get_logger(__name__)

def load_and_merge_raw_data() -> pd.DataFrame:
    """
    Loads all lap, weather, and telemetry files and merges them by index/row.
    Since we saved them concurrently, the row indices should match exactly 
    within each session file.
    """
    logger.info("Discovering raw data files...")
    
    laps_dir = RAW_DATA_DIR / "laps"
    weather_dir = RAW_DATA_DIR / "weather"
    telemetry_dir = RAW_DATA_DIR / "telemetry"
    
    lap_files = glob.glob(str(laps_dir / "*.csv"))
    
    all_sessions = []
    
    for lap_file in lap_files:
        path = Path(lap_file)
        file_name = path.name
        
        weather_file = weather_dir / file_name
        telemetry_file = telemetry_dir / file_name
        
        try:
            laps_df = pd.read_csv(lap_file)
            
            if weather_file.exists():
                weather_df = pd.read_csv(weather_file)
                # Concatenate along columns
                laps_df = pd.concat([laps_df, weather_df], axis=1)
                
            if telemetry_file.exists():
                telemetry_df = pd.read_csv(telemetry_file)
                laps_df = pd.concat([laps_df, telemetry_df], axis=1)
                
            all_sessions.append(laps_df)
        except Exception as e:
            logger.error(f"Error loading {file_name}: {e}")
            
    if not all_sessions:
        logger.warning("No data found to build master dataset.")
        return pd.DataFrame()
        
    master_df = pd.concat(all_sessions, ignore_index=True)
    logger.info(f"Loaded {len(master_df)} total rows across {len(all_sessions)} sessions.")
    return master_df

def data_validation_report(df: pd.DataFrame):
    """
    Prints missing value reports and duplicate checks.
    """
    logger.info("--- Data Quality Report ---")
    
    # 1. Duplicates
    dup_count = df.duplicated().sum()
    logger.info(f"Duplicate Rows: {dup_count}")
    
    # 2. Missing Values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_report = pd.DataFrame({'Missing Count': missing, 'Missing %': missing_pct})
    missing_report = missing_report[missing_report['Missing Count'] > 0].sort_values(by='Missing %', ascending=False)
    
    logger.info("\nMissing Value Report:")
    if not missing_report.empty:
        print(missing_report.head(20)) # Print top 20 missing columns
    else:
        logger.info("No missing values found!")
        
    logger.info("---------------------------")

def clean_and_impute(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes duplicates and handles missing values.
    """
    logger.info("Cleaning and imputing missing values...")
    
    # Drop duplicates
    df = df.drop_duplicates()
    
    # Essential tracking columns that cannot be null
    essential_cols = ['Year', 'EventName', 'SessionType', 'Driver', 'LapNumber']
    df = df.dropna(subset=[col for col in essential_cols if col in df.columns])
    
    # Impute numeric columns with median (grouped by Circuit and SessionType if possible)
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    
    # Impute telemetry and weather features broadly
    for col in numeric_cols:
        if df[col].isnull().any():
            # Fill with global median for simplicity, can be upgraded to grouped median
            df[col] = df[col].fillna(df[col].median())
            
    return df

def main():
    logger.info("Building Master Dataset...")
    
    # 1. Load Data
    raw_df = load_and_merge_raw_data()
    if raw_df.empty:
        return
        
    # 2. Feature Engineering
    engineered_df = run_feature_engineering(raw_df)
    
    # 3. Validation Report (Before Cleaning)
    data_validation_report(engineered_df)
    
    # 4. Clean Data
    clean_df = clean_and_impute(engineered_df)
    
    # 5. Validation Report (After Cleaning)
    data_validation_report(clean_df)
    
    # 6. Save Master Dataset
    output_path = PROCESSED_DATA_DIR / "master_f1_dataset.csv"
    clean_df.to_csv(output_path, index=False)
    logger.info(f"Master dataset saved successfully to {output_path} with shape {clean_df.shape}")

if __name__ == "__main__":
    main()
