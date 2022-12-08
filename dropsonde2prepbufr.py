import sys
sys.path.insert(1, "../dev/plotters/")
from datetime import datetime, timedelta
import glob
import helpers
import pandas as pd
from python_imports import extra
import metpy.calc as mpcalc
from metpy.units import units
from pathlib import Path
import subprocess


start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 28, 18)
frequency = timedelta(hours=6)

prepbufr_dir = lambda date: f"../CPEX-CV/GDAS/{date:%Y%m%d}/"
prepbufr_filename = lambda date: f"gdas_dropsonde.t{date:%H}z.prepbufr.nr"
prepbufr_filename = lambda date: f"gdas_dawn_dropsonde_halo.t{date:%H}z.prepbufr.nr"

dropsonde_dir = "../CPEX-CV/data_preliminary/dropsonde"
dropsonde_prefix = "CPEXCV-dropsonde_DC8_*_RA.nc"

filenames = glob.glob(f"{dropsonde_dir}/{dropsonde_prefix}")
z_keep = helpers.vertical_levels()

for date in pd.date_range(start_date, end_date, freq=frequency):
    print("creating prepbufr for", date)

    start_window = date - frequency / 2
    end_window = date + frequency / 2
    print("searching for dropsondes between", start_window, end_window)

    for filename in sorted(filenames):
        ds, launch_time = extra.get_dropsonde_data(
            filename, subset=["pres", "gpsalt"])
        ds_mass, _ = extra.get_dropsonde_data(
            filename, subset=["pres", "tdry", "mr", "gpsalt"])
        ds_wind, _ = extra.get_dropsonde_data(
            filename, subset=["pres", "gpsalt", "u_wind", "v_wind"])

        if (launch_time > start_window) & (launch_time < end_window) & (len(ds["pres"]) > 0):
            dt = (launch_time - date).days * 24 + (launch_time - date).seconds / 3600
            print("found dropsonde at", launch_time, "dt =", dt)
            lon = ds["lon"].mean()
            lat = ds["lat"].mean()

            ds_mass["Specific_Humidity"] = mpcalc.specific_humidity_from_mixing_ratio(
                ds_mass["mr"])
            if len(ds_mass["pres"]) > 0:
                min_z_mass = ds_mass["gpsalt"].min()
                max_z_mass = ds_mass["gpsalt"].max()
            if len(ds_wind["pres"]) > 0:
                min_z_wind = ds_wind["gpsalt"].min()
                max_z_wind = ds_wind["gpsalt"].max()

            POBmass = []
            POBwind = []
            QOB = []
            TOB = []
            ZOBmass = []
            ZOBwind = []
            UOB = []
            VOB = []

            for dz, z in zip((z_keep[1:] - z_keep[:-1]) * units("meter"), z_keep[1:] * units("meter")):
                if len(ds_mass["pres"]) > 0:
                    if (z > min_z_mass) & (z + 1.1 * dz < max_z_mass):
                        averages = mpcalc.mean_pressure_weighted(
                            ds_mass["pres"], ds_mass["pres"],
                            ds_mass["Specific_Humidity"], ds_mass["tdry"],
                            ds_mass["gpsalt"], height=ds_mass["gpsalt"],
                            bottom=z, depth=dz)
                        POBmass.append(averages[0].to(units("millibar")).m)
                        QOB.append(averages[1].to(units("milligrams / kilogram")).m)
                        TOB.append(averages[2].to(units("celsius")).m)
                        ZOBmass.append(averages[3].to(units("meter")).m)
                if len(ds_wind["pres"]) > 0:
                    if (z > min_z_wind) & (z + 1.1 * dz < max_z_wind):
                        averages = mpcalc.mean_pressure_weighted(
                            ds_wind["pres"], ds_wind["pres"], ds_wind["gpsalt"],
                            ds_wind["u_wind"], ds_wind["v_wind"],
                            height=ds_wind["gpsalt"], bottom=z, depth=dz)
                        POBwind.append(averages[0].to(units("millibar")).m)
                        ZOBwind.append(averages[1].to(units("meter")).m)
                        UOB.append(averages[2].to(units("meter / second")).m)
                        VOB.append(averages[3].to(units("meter / second")).m)
            
            df_averaged_mass = pd.DataFrame({
                "POB": POBmass, "QOB": QOB, "TOB": TOB, "ZOB": ZOBmass})
            df_averaged_mass.to_csv(
                "dropsonde_processed_mass.csv", index=False, header=False)
            df_averaged_wind = pd.DataFrame({
                "POB": POBwind, "ZOB": ZOBwind, "UOB": UOB, "VOB": VOB})
            df_averaged_wind.to_csv(
                "dropsonde_processed_wind.csv", index=False, header=False)

            if (len(POBmass) or len(POBwind)):
                print(len(POBmass), len(POBwind))
                print("adding data to", prepbufr_filename(date))
                Path(prepbufr_dir(date)).mkdir(parents=True, exist_ok=True)
                subprocess.run(
                    ["./prepbufr_encode_upperair_dropsonde.exe",
                    f"{prepbufr_dir(date)}/{prepbufr_filename(date)}",
                    f"{date:%Y%m%d%H}", f"{lon + 360}",
                    f"{lat}", f"{dt}", "dropsonde_processed_mass.csv",
                    "dropsonde_processed_wind.csv", str(len(POBmass)),
                    str(len(POBwind))])
