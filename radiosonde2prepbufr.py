import config
import sys
sys.path.insert(1, "../plotters_cv/")
from datetime import datetime, timedelta
import glob
import pandas as pd
import numpy as np
from python_imports import extra
import metpy.calc as mpcalc
from metpy.units import units
from pathlib import Path
import subprocess


subprocess.run(f"cp {config.radiosonde_data_dir}/{config.radiosonde_prefix} /tmp", shell=True)
subprocess.run("cp prepbufr_encode_upperair_radiosonde.exe /tmp", shell=True)
subprocess.run("cp -r lib /tmp", shell=True)
for date in pd.date_range(
    config.start_date, config.end_date, freq=config.frequency):
    Path(f"/tmp/prepbufr_{date:%Y%m%d}/").mkdir(parents=True, exist_ok=True)
    for prepbufr_filename in config.radiosonde_prepbufr_filenames:
        subprocess.run(
            f"cp {config.prepbufr_dir(date)}/{prepbufr_filename(date)} /tmp/prepbufr_{date:%Y%m%d}/",
            shell=True)

filenames = glob.glob(f"/tmp/{config.radiosonde_prefix}")
z_keep = extra.vertical_levels(config.num_levels)

for date in pd.date_range(
    config.start_date, config.end_date, freq=config.frequency):
    print("creating prepbufr for", date)
    start_window = date - config.frequency / 2
    end_window = date + config.frequency / 2
    print("searching for radiosondes between", start_window, end_window)

    for filename in sorted(filenames):
        df, launch_time = extra.get_radiosonde_data(
            filename, subset=["PRES", "HGHT"])
        df_mass, _ = extra.get_radiosonde_data(
            filename, subset=["PRES", "VTEM", "DWPT", "HGHT"])
        df_wind, _ = extra.get_radiosonde_data(
            filename, subset=["PRES", "HGHT", "UWND", "VWND"])

        if (launch_time > start_window) & (launch_time < end_window) & (len(df["PRES"]) > 0):
            dt = (launch_time - date).days * 24 + (launch_time - date).seconds / 3600
            print("found radiosonde at", launch_time, "dt =", dt)
            lon = round(df["LONG"].mean(), 1)
            lat = round(df["LATI"].mean(), 1)

            cycle = date

            df_mass["Specific_Humidity"] = mpcalc.specific_humidity_from_dewpoint(
                df_mass["PRES"], df_mass["DWPT"])

            if len(df_mass["PRES"]):
                min_p_mass = df_mass["PRES"].min()
                max_p_mass = df_mass["PRES"].max()
                min_z_mass = df_mass["HGHT"].min()
                max_z_mass = df_mass["HGHT"].max()

            if len(df_wind["PRES"]):
                min_p_wind = df_wind["PRES"].min()
                max_p_wind = df_wind["PRES"].max()
                min_z_wind = df_wind["HGHT"].min()
                max_z_wind = df_wind["HGHT"].max()

            POBmass = []
            POBwind = []
            QOB = []
            TOB = []
            ZOBmass = []
            ZOBwind = []
            UOB = []
            VOB = []

            for dz, z in zip((z_keep[1:] - z_keep[:-1]) * units("meter"), z_keep[1:] * units("meter")):
                if (len(df_mass["PRES"]) and (z > min_z_mass) and
                    (z + 1.1 * dz < max_z_mass) and
                    df_mass["HGHT"][np.logical_and(
                        df_mass["HGHT"] > z, df_mass["HGHT"] < z + dz)].any()):
                    averages = mpcalc.mean_pressure_weighted(
                        df_mass["PRES"], df_mass["PRES"],
                        df_mass["Specific_Humidity"], df_mass["VTEM"],
                        df_mass["HGHT"], height=df_mass["HGHT"],
                        bottom=z, depth=dz)
                    POBmass.append(averages[0].to(units("millibar")).m)
                    QOB.append(averages[1].to(units("milligrams / kilogram")).m)
                    TOB.append(averages[2].to(units("celsius")).m)
                    ZOBmass.append(averages[3].to(units("meter")).m)
                if (len(df_wind["PRES"]) and (z > min_z_wind) and
                    (z + 1.1 * dz < max_z_wind) and
                    df_wind["HGHT"][np.logical_and(
                        df_wind["HGHT"] > z, df_wind["HGHT"] < z + dz)].any()):
                    averages = mpcalc.mean_pressure_weighted(
                        df_wind["PRES"], df_wind["PRES"], df_wind["HGHT"],
                        df_wind["UWND"], df_wind["VWND"],
                        height=df_wind["HGHT"], bottom=z, depth=dz)
                    POBwind.append(averages[0].to(units("millibar")).m)
                    ZOBwind.append(averages[1].to(units("meter")).m)
                    UOB.append(averages[2].to(units("meter / second")).m)
                    VOB.append(averages[3].to(units("meter / second")).m)
            
            df_averaged_mass = pd.DataFrame({
                "POB": POBmass,
                "QOB": QOB,
                "TOB": TOB,
                "ZOB": ZOBmass}).sort_values("POB", ascending=False)
            if "QOB" in config.deny_variables:
                df_averaged_mass = df_averaged_mass.assign(QOB=np.nan)
            if "TOB" in config.deny_variables:
                df_averaged_mass = df_averaged_mass.assign(TOB=np.nan)
            df_averaged_mass.dropna(
                subset=["QOB", "TOB"], how="all", inplace=True)
            df_averaged_mass.to_csv(
                "/tmp/radiosonde_processed_mass.csv", index=False, header=False)
            df_averaged_wind = pd.DataFrame({
                "POB": POBwind,
                "ZOB": ZOBwind,
                "UOB": UOB,
                "VOB": VOB}).sort_values("POB", ascending=False)
            if "UOB" in config.deny_variables:
                df_averaged_wind = df_averaged_wind.assign(UOB=np.nan)
            if "VOB" in config.deny_variables:
                df_averaged_wind = df_averaged_wind.assign(VOB=np.nan)
            df_averaged_wind.dropna(
                subset=["UOB", "VOB"], how="all", inplace=True)
            df_averaged_wind.to_csv(
                "/tmp/radiosonde_processed_wind.csv", index=False, header=False)

            if df_averaged_mass.size or df_averaged_wind.size:
                print(df_averaged_mass.size, df_averaged_wind.size)

                for prepbufr_filename in config.radiosonde_prepbufr_filenames:
                    print("adding data to", prepbufr_filename(date))
                    Path(config.prepbufr_dir(date)).mkdir(
                        parents=True, exist_ok=True)
                    subprocess.run(
                        ["/tmp/prepbufr_encode_upperair_radiosonde.exe",
                        f"/tmp/prepbufr_{cycle:%Y%m%d}/{prepbufr_filename(cycle)}",
                        f"{cycle:%Y%m%d%H}", f"{lon}", f"{lat}", f"{dt}",
                        "/tmp/radiosonde_processed_mass.csv",
                        "/tmp/radiosonde_processed_wind.csv",
                        str(df_averaged_mass.size),
                        str(df_averaged_wind.size)])

subprocess.run(f"rm /tmp/{config.radiosonde_prefix}", shell=True)
subprocess.run(f"rm /tmp/radiosonde_processed_mass.csv", shell=True)
subprocess.run(f"rm /tmp/radiosonde_processed_wind.csv", shell=True)
subprocess.run(f"rm -rf /tmp/lib", shell=True)
subprocess.run(f"rm /tmp/prepbufr_encode_upperair_radiosonde.exe", shell=True)
for date in pd.date_range(config.start_date, config.end_date, freq="1d"):
    subprocess.run(
        f"mv /tmp/prepbufr_{date:%Y%m%d}/* {config.prepbufr_dir(date)}",
        shell=True)
    subprocess.run(f"rm -rf /tmp/prepbufr_{date:%Y%m%d}", shell=True)
