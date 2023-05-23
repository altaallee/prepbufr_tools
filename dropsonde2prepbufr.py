import sys
sys.path.insert(1, "../plotters_cv/")
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
end_date = datetime(2022, 9, 30, 18)
frequency = timedelta(hours=6)

prepbufr_dir = lambda date: f"../CPEX-CV/GDAS_R0_HALO_R1/{date:%Y%m%d}/"
prepbufr_filenames = [
    lambda date: f"gdas_dropsonde.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_dropsonde_halo.t{date:%H}z.prepbufr.nr",
    lambda date: f"dropsonde.t{date:%H}z.prepbufr.nr",
]

dropsonde_dir = "../CPEX-CV/data_R0/dropsonde/"
dropsonde_prefix = "CPEX_AVAPS_RD41_v1_2022*"
decoded_gdas_dropsonde_dir = "decoded_gdas_dropsonde_text"

subprocess.run(f"cp {dropsonde_dir}/{dropsonde_prefix} /tmp", shell=True)
subprocess.run("cp prepbufr_encode_upperair_dropsonde.exe /tmp", shell=True)
subprocess.run("cp -r lib /tmp", shell=True)
for date in pd.date_range(start_date, end_date, freq=frequency):
    Path(f"/tmp/prepbufr_{date:%Y%m%d}/").mkdir(parents=True, exist_ok=True)
    for prepbufr_filename in prepbufr_filenames:
        subprocess.run(
            f"cp {prepbufr_dir(date)}/{prepbufr_filename(date)} /tmp/prepbufr_{date:%Y%m%d}/",
            shell=True)

filenames = glob.glob(f"/tmp/{dropsonde_prefix}")
z_keep = helpers.vertical_levels()

for date in pd.date_range(start_date, end_date, freq=frequency):
    print("creating prepbufr for", date)
    start_window = date - frequency / 2
    end_window = date + frequency / 2
    print("searching for dropsondes between", start_window, end_window)

    for filename in sorted(filenames):
        ds, launch_time = extra.get_dropsonde_data(
            filename, subset=["pres", "alt"])
        ds_mass, _ = extra.get_dropsonde_data(
            filename, subset=["pres", "vt", "mr", "alt"])
        ds_wind, _ = extra.get_dropsonde_data(
            filename, subset=["pres", "alt", "u_wind", "v_wind"])

        if (launch_time > start_window) & (launch_time < end_window) & (len(ds["pres"]) > 0):
            dt = (launch_time - date).days * 24 + (launch_time - date).seconds / 3600
            print("found dropsonde at", launch_time, "dt =", dt)
            lon = round(ds["reference_lon"][0] + 360, 1)
            lat = round(ds["reference_lat"][0], 1)

            ds_mass["Specific_Humidity"] = mpcalc.specific_humidity_from_mixing_ratio(
                ds_mass["mr"])

            if len(ds_mass["pres"]):
                min_z_mass = ds_mass["alt"].min()
                max_z_mass = ds_mass["alt"].max()

                match_mass = glob.glob(
                    f"{decoded_gdas_dropsonde_dir}/sonde_{date:%Y%m%d}??_132_{lon}_{lat}_*")
                if len(match_mass) == 1:
                    _, cycle, _, lon, lat, dt = match_mass[0].split("/")[-1].split("_")
                    print("Found mass dropsonde at cycle", cycle)
                    df_gdas_mass = pd.read_csv(match_mass[0])
                    mass_exist = True
                    cycle = datetime.strptime(cycle, "%Y%m%d%H")
                elif len(match_mass) == 0:
                    print("Failed to find mass dropsonde")
                    mass_exist = False
                    cycle = date

            if len(ds_wind["pres"]):
                min_z_wind = ds_wind["alt"].min()
                max_z_wind = ds_wind["alt"].max()

                match_wind = glob.glob(
                    f"{decoded_gdas_dropsonde_dir}/sonde_{date:%Y%m%d}??_232_{lon}_{lat}_*")
                if len(match_wind) == 1:
                    _, cycle, _, lon, lat, dt = match_wind[0].split("/")[-1].split("_")
                    print("Found wind dropsonde at cycle", cycle)
                    df_gdas_wind = pd.read_csv(match_wind[0])
                    wind_exist = True
                    cycle = datetime.strptime(cycle, "%Y%m%d%H")
                elif len(match_wind) == 0:
                    print("Failed to find wind dropsonde")
                    wind_exist = False
                    cycle = date

            if len(ds_mass["pres"]) & ((not mass_exist) & (not wind_exist)):
                POBmass = [ds_mass["pres"][0].to(units("millibar")).m]
                POBwind = [ds_mass["pres"][0].to(units("millibar")).m]
                QOB = [ds_mass["Specific_Humidity"][0].to(units("milligrams / kilogram")).m]
                TOB = [ds_mass["vt"][0].to(units("celsius")).m]
                ZOBmass = [ds_mass["alt"][0].to(units("meter")).m]
                ZOBwind = [ds_mass["alt"][0].to(units("meter")).m]
                UOB = [10**10]
                VOB = [10**10]
            else:
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
                            ds_mass["Specific_Humidity"], ds_mass["vt"],
                            ds_mass["alt"], height=ds_mass["alt"],
                            bottom=z, depth=dz)
                        prs = averages[0].to(units("millibar")).m
                        if mass_exist & (abs(df_gdas_mass["pres"] - prs) < 10).any():
                            print("Skipping mass preesure level", prs) 
                            continue
                        POBmass.append(prs)
                        QOB.append(averages[1].to(units("milligrams / kilogram")).m)
                        TOB.append(averages[2].to(units("celsius")).m)
                        ZOBmass.append(averages[3].to(units("meter")).m)
                if len(ds_wind["pres"]) > 0:
                    if (z > min_z_wind) & (z + 1.1 * dz < max_z_wind):
                        averages = mpcalc.mean_pressure_weighted(
                            ds_wind["pres"], ds_wind["pres"], ds_wind["alt"],
                            ds_wind["u_wind"], ds_wind["v_wind"],
                            height=ds_wind["alt"], bottom=z, depth=dz)
                        prs = averages[0].to(units("millibar")).m
                        if wind_exist & (abs(df_gdas_wind["pres"] - prs) < 10).any():
                            print("Skipping wind preesure level", prs)
                            continue
                        POBwind.append(averages[0].to(units("millibar")).m)
                        ZOBwind.append(averages[1].to(units("meter")).m)
                        UOB.append(averages[2].to(units("meter / second")).m)
                        VOB.append(averages[3].to(units("meter / second")).m)
            
            df_averaged_mass = pd.DataFrame({
                "POB": POBmass, "QOB": QOB, "TOB": TOB, "ZOB": ZOBmass})
            df_averaged_mass.to_csv(
                "/tmp/dropsonde_processed_mass.csv", index=False, header=False)
            df_averaged_wind = pd.DataFrame({
                "POB": POBwind, "ZOB": ZOBwind, "UOB": UOB, "VOB": VOB})
            df_averaged_wind.to_csv(
                "/tmp/dropsonde_processed_wind.csv", index=False, header=False)

            if (len(POBmass) or len(POBwind)):
                print(len(POBmass), len(POBwind))

                for prepbufr_filename in prepbufr_filenames:
                    print("adding data to", prepbufr_filename(date))
                    Path(prepbufr_dir(date)).mkdir(parents=True, exist_ok=True)
                    subprocess.run(
                        ["/tmp/prepbufr_encode_upperair_dropsonde.exe",
                        f"/tmp/prepbufr_{cycle:%Y%m%d}/{prepbufr_filename(cycle)}",
                        f"{cycle:%Y%m%d%H}", f"{lon}", f"{lat}", f"{dt}",
                        "/tmp/dropsonde_processed_mass.csv",
                        "/tmp/dropsonde_processed_wind.csv", str(len(POBmass)),
                        str(len(POBwind))])

subprocess.run(f"rm /tmp/{dropsonde_prefix}", shell=True)
for date in pd.date_range(start_date, end_date, freq="1d"):
    subprocess.run(
        f"mv /tmp/prepbufr_{date:%Y%m%d}/* {prepbufr_dir(date)}", shell=True)
