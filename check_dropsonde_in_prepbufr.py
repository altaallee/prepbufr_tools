import sys
sys.path.insert(1, "../plotters_cv/")
from python_imports import extra
from datetime import datetime, timedelta
import pandas as pd
import glob


start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 30, 18)
freq = timedelta(hours=6)

dropsonde_dir = "../CPEX-CV/data_R0/dropsonde/"
dropsonde_prefix = "CPEX_AVAPS_RD41_v1_2022*"
decoded_output_dir = "decoded_gdas_dropsonde_text"

filenames = glob.glob(f"{dropsonde_dir}/{dropsonde_prefix}")

for date in pd.date_range(start_date, end_date, freq=freq):
    print(date)
    
    start_window = date - freq / 2
    end_window = date + freq / 2
    
    for filename in sorted(filenames):
        df, launch_time = extra.get_dropsonde_data(filename)

        if (launch_time > start_window) & (launch_time < end_window):
            lon = round(df["reference_lon"][0] + 360, 1)
            lat = round(df["reference_lat"][0], 1)
            reference_time = df["reference_time"][0]
            match_mass = glob.glob(
                f"{decoded_output_dir}/sonde_{date:%Y%m%d}??_132_{lon}_{lat}_*")
            if len(match_mass) == 1:
                _, cycle_time, _, lon, lat, dtime = match_mass[0].split("/")[-1].split("_")
                print(
                    "Found mass sonde at cycle", cycle_time, "lon", lon, "lat",
                    lat, "dtime", dtime)
            elif len(match_mass) == 0:
                print(
                    "Failed to find sonde for", reference_time, "lon", lon,
                    "lat", lat)
            else:
                print(
                    "Found multiple possible mass sondes for", reference_time,
                    "lon", lon, "lat", lat)

            match_wind = glob.glob(
                f"{decoded_output_dir}/sonde_{date:%Y%m%d}??_232_{lon}_{lat}_*")
            if len(match_wind) == 1:
                _, cycle_time, _, lon, lat, dtime = match_wind[0].split("/")[-1].split("_")
                print(
                    "Found wind sonde at cycle", cycle_time, "lon", lon, "lat",
                    lat, "dtime", dtime)
            elif len(match_wind) == 0:
                print(
                    "Failed to find sonde for", reference_time, "lon", lon,
                    "lat", lat)
            else:
                print(
                    "Found multiple possible wind sondes for", reference_time,
                    "lon", lon, "lat", lat)
