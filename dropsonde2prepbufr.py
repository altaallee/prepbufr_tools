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


subprocess.run(
    f"cp {config.dropsonde_data_dir}/{config.dropsonde_prefix} /tmp", shell=True)
subprocess.run("cp prepbufr_encode_upperair_dropsonde.exe /tmp", shell=True)
subprocess.run("cp -r lib /tmp", shell=True)
subprocess.run(f"cp {config.decoded_gdas_dropsonde_dir}/* /tmp", shell=True)
for date in pd.date_range(
    config.start_date, config.end_date, freq=config.frequency):
    Path(f"/tmp/prepbufr_{date:%Y%m%d}/").mkdir(parents=True, exist_ok=True)
    for prepbufr_filename in config.dropsonde_prepbufr_filenames:
        subprocess.run(
            f"cp {config.prepbufr_dir(date)}/{prepbufr_filename(date)} /tmp/prepbufr_{date:%Y%m%d}/",
            shell=True)

filenames = glob.glob(f"/tmp/{config.dropsonde_prefix}")
z_keep = extra.vertical_levels(config.num_levels)

if config.num_levels_dropsonde == 60:
    prs_condition = lambda prs: -9 * 10**-5 * prs ** 2 + 0.1125 * prs - 16
elif config.num_levels_dropsonde == 45:
    prs_condition = lambda prs: 1.1772615755*10**-15*prs**6 - 5.6433647319*10**-12*prs**5 + 9.8569456543*10**-9*prs**4 - 8.3496759069*10**-6*prs**3 + 3.6593810943*10**-3*prs**2 - 7.7141293332*10**-1*prs + 7.6700274216E+01
elif config.num_levels_dropsonde == "model":
    df = pd.read_csv("sounding_model_levels.csv")
    p = np.polyfit(df["pres_avg"], df["pres_diff"], 5)
    prs_condition = lambda prs: np.poly1d(p)(prs)

for date in pd.date_range(
    config.start_date, config.end_date, freq=config.frequency):
    print("creating prepbufr for", date)
    start_window = date - config.frequency / 2
    end_window = date + config.frequency / 2
    print("searching for dropsondes between", start_window, end_window)

    for filename in sorted(filenames):
        df, launch_time = extra.get_dropsonde_data(
            filename, subset=["pres", "alt"])
        df_mass, _ = extra.get_dropsonde_data(
            filename, subset=["pres", "vt", "mr", "alt"])
        df_wind, _ = extra.get_dropsonde_data(
            filename, subset=["pres", "alt", "u_wind", "v_wind"])

        if (launch_time > start_window) & (launch_time < end_window) & (len(df["pres"]) > 0):
            dt = (launch_time - date).days * 24 + (launch_time - date).seconds / 3600
            print("found dropsonde at", launch_time, "dt =", dt)
            lon = round(df["reference_lon"][0] + 360, 1)
            lat = round(df["reference_lat"][0], 1)

            df_mass["Specific_Humidity"] = mpcalc.specific_humidity_from_mixing_ratio(
                df_mass["mr"])

            if len(df_mass["pres"]):
                min_p_mass = df_mass["pres"].min()
                max_p_mass = df_mass["pres"].max()
                min_z_mass = df_mass["alt"].min()
                max_z_mass = df_mass["alt"].max()

                match_mass = glob.glob(
                    f"/tmp/sonde_{date:%Y%m%d}??_132_{lon}_{lat}_*")
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

            if len(df_wind["pres"]):
                min_p_wind = df_wind["pres"].min()
                max_p_wind = df_wind["pres"].max()
                min_z_wind = df_wind["alt"].min()
                max_z_wind = df_wind["alt"].max()

                match_wind = glob.glob(
                    f"/tmp/sonde_{date:%Y%m%d}??_232_{lon}_{lat}_*")
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

            if len(df_mass["pres"]) & ((not mass_exist) & (not wind_exist)):
                POBmass = [df_mass["pres"][0].to(units("millibar")).m]
                POBwind = [df_mass["pres"][0].to(units("millibar")).m]
                QOB = [df_mass["Specific_Humidity"][0].to(units("milligrams / kilogram")).m]
                TOB = [df_mass["vt"][0].to(units("celsius")).m]
                ZOBmass = [df_mass["alt"][0].to(units("meter")).m]
                ZOBwind = [df_mass["alt"][0].to(units("meter")).m]
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
                if (len(df_mass["pres"]) and (z > min_z_mass) and
                    (z + 1.1 * dz < max_z_mass) and
                    df_mass["alt"][np.logical_and(
                        df_mass["alt"] > z, df_mass["alt"] < z + dz)].any()):
                    averages = mpcalc.mean_pressure_weighted(
                        df_mass["pres"], df_mass["pres"],
                        df_mass["Specific_Humidity"], df_mass["vt"],
                        df_mass["alt"], height=df_mass["alt"],
                        bottom=z, depth=dz)
                    prs = averages[0].to(units("millibar")).m
                    if not (mass_exist and (abs(df_gdas_mass["pres"] - prs) < prs_condition(prs)).any()):
                        POBmass.append(prs)
                        QOB.append(averages[1].to(units("milligrams / kilogram")).m)
                        TOB.append(averages[2].to(units("celsius")).m)
                        ZOBmass.append(averages[3].to(units("meter")).m)
                    else:
                        print("Skipping mass preesure level", prs) 
                if (len(df_wind["pres"]) and (z > min_z_wind) and
                    (z + 1.1 * dz < max_z_wind) and
                    df_wind["alt"][np.logical_and(
                        df_wind["alt"] > z, df_wind["alt"] < z + dz)].any()):
                    averages = mpcalc.mean_pressure_weighted(
                        df_wind["pres"], df_wind["pres"], df_wind["alt"],
                        df_wind["u_wind"], df_wind["v_wind"],
                        height=df_wind["alt"], bottom=z, depth=dz)
                    prs = averages[0].to(units("millibar")).m
                    if not(wind_exist and (abs(df_gdas_wind["pres"] - prs) < prs_condition(prs)).any()):
                        POBwind.append(averages[0].to(units("millibar")).m)
                        ZOBwind.append(averages[1].to(units("meter")).m)
                        UOB.append(averages[2].to(units("meter / second")).m)
                        VOB.append(averages[3].to(units("meter / second")).m)
                    else:
                        print("Skipping wind preesure level", prs)
            
            if len(df_mass["pres"]) and mass_exist:
                df_mass_levels = pd.concat(
                    [pd.Series(POBmass), df_gdas_mass["pres"]]).sort_values(
                        ignore_index=True).to_frame("pres")
                df_mass_levels["current_dp"] = df_mass_levels["pres"].diff()
                df_mass_levels["mid_pres"] = df_mass_levels["pres"].rolling(2).mean()
                df_mass_levels["expected_dp"] = df_mass_levels["mid_pres"].apply(prs_condition)
                df_mass_levels = df_mass_levels[df_mass_levels["current_dp"] > 1.75 * df_mass_levels["expected_dp"]]
                for _, row in df_mass_levels.iterrows():
                    if ((row["mid_pres"] - row["expected_dp"] / 2) * units("millibar") > min_p_mass and
                        (row["mid_pres"] + row["expected_dp"] / 2) * units("millibar") < max_p_mass):
                        averages = mpcalc.mean_pressure_weighted(
                            df_mass["pres"], df_mass["pres"],
                            df_mass["Specific_Humidity"], df_mass["vt"],
                            df_mass["alt"], height=df_mass["alt"],
                            bottom=(row["mid_pres"] + row["expected_dp"] / 2) * units("millibar"),
                            depth=row["expected_dp"] * units("millibar"))
                        POBmass.append(averages[0].to(units("millibar")).m)
                        QOB.append(averages[1].to(units("milligrams / kilogram")).m)
                        TOB.append(averages[2].to(units("celsius")).m)
                        ZOBmass.append(averages[3].to(units("meter")).m)
            if len(df_wind["pres"]) and wind_exist:
                df_wind_levels = pd.concat(
                    [pd.Series(POBwind), df_gdas_wind["pres"]]).sort_values(
                        ignore_index=True).to_frame("pres")
                df_wind_levels["current_dp"] = df_wind_levels["pres"].diff()
                df_wind_levels["mid_pres"] = df_wind_levels["pres"].rolling(2).mean()
                df_wind_levels["expected_dp"] = df_wind_levels["mid_pres"].apply(prs_condition)
                df_wind_levels = df_wind_levels[df_wind_levels["current_dp"] > 1.75 * df_wind_levels["expected_dp"]]
                for _, row in df_wind_levels.iterrows():
                    if ((row["mid_pres"] - row["expected_dp"] / 2) * units("millibar") > min_p_wind and
                        (row["mid_pres"] + row["expected_dp"] / 2) * units("millibar") < max_p_wind):
                        averages = mpcalc.mean_pressure_weighted(
                            df_wind["pres"], df_wind["pres"], df_wind["alt"],
                            df_wind["u_wind"], df_wind["v_wind"],
                            height=df_wind["alt"],
                            bottom=(row["mid_pres"] + row["expected_dp"] / 2) * units("millibar"),
                            depth=row["expected_dp"] * units("millibar"))
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
            df_averaged_mass.fillna(10e10, inplace=True)
            df_averaged_mass.to_csv(
                "/tmp/dropsonde_processed_mass.csv", index=False, header=False)
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
            df_averaged_wind.fillna(10e10, inplace=True)
            df_averaged_wind.to_csv(
                "/tmp/dropsonde_processed_wind.csv", index=False, header=False)

            if df_averaged_mass.size or df_averaged_wind.size:
                print(df_averaged_mass.size, df_averaged_wind.size)

                for prepbufr_filename in config.dropsonde_prepbufr_filenames:
                    print("adding data to", prepbufr_filename(date))
                    Path(config.prepbufr_dir(date)).mkdir(
                        parents=True, exist_ok=True)
                    subprocess.run(
                        ["/tmp/prepbufr_encode_upperair_dropsonde.exe",
                        f"/tmp/prepbufr_{cycle:%Y%m%d}/{prepbufr_filename(cycle)}",
                        f"{cycle:%Y%m%d%H}", f"{lon}", f"{lat}", f"{dt}",
                        "/tmp/dropsonde_processed_mass.csv",
                        "/tmp/dropsonde_processed_wind.csv",
                        str(df_averaged_mass.size),
                        str(df_averaged_wind.size)])

subprocess.run(f"rm /tmp/{config.dropsonde_prefix}", shell=True)
subprocess.run(f"rm /tmp/sonde*", shell=True)
subprocess.run(f"rm /tmp/dropsonde_processed_mass.csv", shell=True)
subprocess.run(f"rm /tmp/dropsonde_processed_wind.csv", shell=True)
subprocess.run(f"rm /tmp/prepbufr_encode_upperair_dropsonde.exe", shell=True)
subprocess.run(f"rm -rf /tmp/lib", shell=True)
for date in pd.date_range(config.start_date, config.end_date, freq="1d"):
    subprocess.run(
        f"mv /tmp/prepbufr_{date:%Y%m%d}/* {config.prepbufr_dir(date)}",
        shell=True)
    subprocess.run(f"rm -rf /tmp/prepbufr_{date:%Y%m%d}", shell=True)
