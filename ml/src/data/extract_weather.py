import pandas as pd

def extract_weather_data(laps_df) -> pd.DataFrame:
    """
    Extracts weather data for each lap in the dataframe.
    FastF1's get_weather_data() automatically interpolates the 1-minute weather 
    measurements to the specific start time of each lap.
    """
    try:
        # This returns AirTemp, TrackTemp, Humidity, Pressure, WindSpeed, WindDirection, Rainfall
        weather_data = laps_df.get_weather_data()
        
        # Keep only the requested columns
        keep_cols = ['AirTemp', 'TrackTemp', 'Humidity', 'WindSpeed', 'Rainfall']
        
        # Filter available columns just in case some are missing in older seasons
        available_cols = [col for col in keep_cols if col in weather_data.columns]
        
        return weather_data[available_cols]
    except Exception as e:
        # If weather extraction fails, return empty DataFrame
        return pd.DataFrame()
