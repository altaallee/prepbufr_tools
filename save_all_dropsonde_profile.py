import sys
sys.path.insert(1, "../plotters_cv/")
from python_imports import extra
from datetime import datetime
import glob
from pathlib import Path
import pandas as pd


start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 30, 18)

dropsonde_dir = "../CPEX-CV/data_R0/dropsonde/"
dropsonde_prefix = "CPEX_AVAPS_RD41_v1_202209*"
decoded_appended_dropsonde_dir = "decoded_appended_dropsonde_text"
decoded_gdas_dropsonde_dir = "decoded_gdas_dropsonde_text"
output_dir = "dropsonde_in_prepbufr_data"

filenames = glob.glob(f"{dropsonde_dir}/{dropsonde_prefix}*")

Path(output_dir).mkdir(parents=True, exist_ok=True)

mass_data = pd.DataFrame()
wind_data = pd.DataFrame()

for filename in sorted(filenames):
    print(filename)

    df, launch_time = extra.get_dropsonde_data(filename, subset="pres")

    if (launch_time > start_date) and (launch_time < end_date) and (len(df["pres"])):
        lon = round(df["reference_lon"][0] + 360, 1)
        lat = round(df["reference_lat"][0], 1)
        date = df["reference_time"][0]

        append_mass_file = glob.glob(
            f"{decoded_appended_dropsonde_dir}/sonde_{date:%Y%m%d}??_132_{lon}_{lat}_*")
        if len(append_mass_file):
            df_mass = pd.read_csv(append_mass_file[0], na_values=[100000000000])
            df_mass["source"] = "append"
            df_mass["lon"] = lon
            df_mass["lat"] = lat
            df_mass["launch_time"] = date
            mass_data = pd.concat([mass_data, df_mass])
        
        append_wind_file = glob.glob(
            f"{decoded_appended_dropsonde_dir}/sonde_{date:%Y%m%d}??_232_{lon}_{lat}_*")
        if len(append_wind_file):
            df_wind = pd.read_csv(append_wind_file[0], na_values=[100000000000])
            df_wind["source"] = "append"
            df_wind["lon"] = lon
            df_wind["lat"] = lat
            df_wind["launch_time"] = date
            wind_data = pd.concat([wind_data, df_wind])

        gdas_mass_file = glob.glob(
            f"{decoded_gdas_dropsonde_dir}/sonde_{date:%Y%m%d}??_132_{lon}_{lat}_*")
        if len(gdas_mass_file):
            df_mass = pd.read_csv(gdas_mass_file[0], na_values=[100000000000])
            df_mass["source"] = "gdas"
            df_mass["lon"] = lon
            df_mass["lat"] = lat
            df_mass["launch_time"] = date
            mass_data = pd.concat([mass_data, df_mass])

        gdas_wind_file = glob.glob(
            f"{decoded_gdas_dropsonde_dir}/sonde_{date:%Y%m%d}??_232_{lon}_{lat}_*")
        if len(gdas_wind_file):
            df_wind = pd.read_csv(gdas_wind_file[0], na_values=[100000000000])
            df_wind["source"] = "gdas"
            df_wind["lon"] = lon
            df_wind["lat"] = lat
            df_wind["launch_time"] = date
            wind_data = pd.concat([wind_data, df_wind])

mass_data.sort_values(["launch_time", "pres"], inplace=True)
wind_data.sort_values(["launch_time", "pres"], inplace=True)

mass_data.to_csv(f"{output_dir}/mass.csv", index=False)
wind_data.to_csv(f"{output_dir}/wind.csv", index=False)
