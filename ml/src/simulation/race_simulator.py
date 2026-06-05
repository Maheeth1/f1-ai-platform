import pandas as pd
import numpy as np
from pathlib import Path
import sys
import copy
from collections import defaultdict
from tqdm import tqdm

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.utils.logger import get_logger
from src.models import registry

logger = get_logger(__name__)

class RaceSimulator:
    def __init__(self, target_name='LapTimeSeconds', version='latest'):
        """
        Initializes the simulator by loading the predictive model from the registry.
        """
        logger.info("Initializing Race Simulator...")
        try:
            self.artifacts = registry.load_model(target_name=target_name, version=version)
            self.model = self.artifacts['model']
            self.features = self.artifacts['features']
            self.metadata = self.artifacts['metadata']
            self.rmse = self.metadata['metrics'][1] # Assuming metric order is [MAE, RMSE, R2]
            logger.info(f"Loaded {self.metadata['model_type']} (v{self.metadata['version']}) with baseline RMSE: {self.rmse:.4f}")
        except Exception as e:
            logger.error(f"Failed to load model artifacts: {e}")
            raise e

    def _prepare_lap_data(self, base_grid_df, current_lap, current_positions, tyre_life_dict):
        """
        Prepares the feature dataframe for the current lap simulation.
        Updates dynamic features like LapNumber, TyreLife, Position.
        """
        lap_df = base_grid_df.copy()
        
        # Update dynamic features
        lap_df['LapNumber'] = current_lap
        lap_df['FuelEffect'] = current_lap * 0.06
        
        for idx, row in lap_df.iterrows():
            driver = row['Driver']
            
            # Update Position
            if 'PrevPosition' in self.features:
                lap_df.at[idx, 'PrevPosition'] = current_positions[driver]
            
            # Update TyreLife
            if 'TyreLife' in self.features:
                lap_df.at[idx, 'TyreLife'] = tyre_life_dict[driver]
                
        # Ensure all required features are present and ordered
        for f in self.features:
            if f not in lap_df.columns:
                lap_df[f] = 0.0 # Default fill for missing historical/telemetry data
                
        # Handle categoricals if needed
        cat_cols = lap_df[self.features].select_dtypes(include=['object']).columns
        for col in cat_cols:
            lap_df[col] = lap_df[col].astype(str).astype('category')
            
        return lap_df[self.features]

    def simulate_single_race(self, starting_grid: pd.DataFrame, total_laps: int, strategies: dict, pit_loss_seconds: float = 22.0) -> dict:
        """
        Simulates a single race instance.
        - strategies: dict mapping Driver -> list of lap numbers to pit on. e.g. {'VER': [20], 'HAM': [18, 35]}
        Returns a dictionary mapping Driver to their final race time.
        """
        drivers = starting_grid['Driver'].tolist()
        cumulative_times = {driver: 0.0 for driver in drivers}
        current_positions = {row['Driver']: row.get('StartingPosition', i+1) for i, row in starting_grid.iterrows()}
        tyre_life_dict = {driver: 1 for driver in drivers}
        
        for lap in range(1, total_laps + 1):
            # 1. Prepare data for this lap
            lap_df = self._prepare_lap_data(starting_grid, lap, current_positions, tyre_life_dict)
            
            # 2. Predict base lap time
            base_lap_times = self.model.predict(lap_df)
            
            # 3. Apply Monte Carlo Variance & Pit Stops
            for i, driver in enumerate(drivers):
                # Add gaussian noise based on model's RMSE (represents unmodeled traffic/mistakes/variance)
                noise = np.random.normal(0, self.rmse)
                lap_time = base_lap_times[i] + noise
                
                # Check for pit stop
                driver_strategy = strategies.get(driver, [])
                if lap in driver_strategy:
                    lap_time += pit_loss_seconds
                    tyre_life_dict[driver] = 1 # Reset tyre life
                else:
                    tyre_life_dict[driver] += 1
                    
                cumulative_times[driver] += lap_time
                
            # 4. Update track positions based on cumulative times
            # Sort drivers by cumulative time
            sorted_drivers = sorted(cumulative_times.keys(), key=lambda d: cumulative_times[d])
            for pos, driver in enumerate(sorted_drivers):
                current_positions[driver] = pos + 1
                
        return cumulative_times

    def run_monte_carlo(self, starting_grid: pd.DataFrame, total_laps: int, strategies: dict, n_simulations: int = 1000):
        """
        Runs multiple Monte Carlo simulations to calculate probabilistic outcomes.
        """
        logger.info(f"Starting {n_simulations} Monte Carlo simulations for {total_laps} laps...")
        
        drivers = starting_grid['Driver'].tolist()
        
        # Track finishing positions across all sims
        # Dict[Driver, List of finishing positions]
        finishing_positions = defaultdict(list)
        
        for sim in tqdm(range(n_simulations), desc="Simulating Races"):
            final_times = self.simulate_single_race(starting_grid, total_laps, strategies)
            
            # Determine final order
            sorted_drivers = sorted(final_times.keys(), key=lambda d: final_times[d])
            for pos, driver in enumerate(sorted_drivers):
                finishing_positions[driver].append(pos + 1)
                
        # Aggregate Results
        results = []
        for driver in drivers:
            positions = np.array(finishing_positions[driver])
            
            win_prob = np.mean(positions == 1) * 100
            podium_prob = np.mean(positions <= 3) * 100
            avg_pos = np.mean(positions)
            
            results.append({
                'Driver': driver,
                'Win_Probability_%': round(win_prob, 2),
                'Podium_Probability_%': round(podium_prob, 2),
                'Average_Position': round(avg_pos, 1)
            })
            
        # Sort by Win Probability
        results_df = pd.DataFrame(results).sort_values(by=['Win_Probability_%', 'Podium_Probability_%'], ascending=False)
        return results_df

if __name__ == "__main__":
    # Demonstration / Standalone testing
    try:
        simulator = RaceSimulator()
        
        # Mock Starting Grid
        mock_grid = pd.DataFrame({
            'Driver': ['VER', 'NOR', 'LEC', 'SAI', 'HAM', 'RUS', 'PER', 'PIA', 'ALO', 'STR'],
            'StartingPosition': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Team': ['Red Bull Racing', 'McLaren', 'Ferrari', 'Ferrari', 'Mercedes', 'Mercedes', 'Red Bull Racing', 'McLaren', 'Aston Martin', 'Aston Martin'],
            'Compound': ['MEDIUM'] * 10,
            'Year': [2024] * 10,
            'EventName': ['Mock Grand Prix'] * 10,
            'SessionType': ['Race'] * 10,
            'IsSafetyCar': [False] * 10,
            'IsVirtualSafetyCar': [False] * 10,
            'AirTemp': [25.0] * 10,
            'TrackTemp': [35.0] * 10,
            'Humidity': [45.0] * 10,
            'WindSpeed': [2.0] * 10,
            'Rainfall': [False] * 10
        })
        
        # Predefined pit strategies (e.g. 1-stop)
        strategies = {
            'VER': [20], 'NOR': [21], 'LEC': [19], 'SAI': [22],
            'HAM': [18], 'RUS': [23], 'PER': [17], 'PIA': [24],
            'ALO': [16], 'STR': [25]
        }
        
        results = simulator.run_monte_carlo(mock_grid, total_laps=50, strategies=strategies, n_simulations=1000)
        
        print("\n=== MONTE CARLO RACE SIMULATION RESULTS ===")
        print(results.to_string(index=False))
        
    except Exception as e:
        logger.error(f"Simulation failed to initialize: {e}")
