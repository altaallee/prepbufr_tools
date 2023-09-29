import config
import sys
sys.path.insert(1, "../plotters_cv/")
from datetime import datetime, timedelta
import pandas as pd
import xarray as xr
from python_imports import extra, wrf_calc
import numpy as np
import subprocess
from pathlib import Path


wrfinput_dir = "/nobackupp28/alee31/CPEX-CV/era5_wrfinput/"

subprocess.run("cp prepbufr_encode_upperair_dawn.exe /tmp", shell=True)
subprocess.run("cp -r lib /tmp", shell=True)

for date in pd.date_range(
    config.start_date, config.end_date, freq=config.frequency):
    Path(f"/tmp/prepbufr_{date:%Y%m%d}/").mkdir(parents=True, exist_ok=True)
    for prepbufr_filename in config.dawn_prepbufr_filenames:
        subprocess.run(
            f"cp {config.prepbufr_dir(date)}/{prepbufr_filename(date)} /tmp/prepbufr_{date:%Y%m%d}/",
            shell=True)

previous_time = None
for dawn_filename in config.dawn_filenames:
    subprocess.run(f"cp {config.dawn_data_dir}/{dawn_filename} /tmp", shell=True)
    ds = xr.load_dataset(f"/tmp/{dawn_filename}")
    ds = ds.sel({"time": ds["time"][::config.skip]})

    for date in pd.date_range(
        config.start_date, config.end_date, freq=config.frequency):
        print("creating prepbufr for", date)

        start_window = date - config.frequency / 2
        end_window = date + config.frequency / 2
        print("searching for DAWN data between", start_window, end_window)

        ds_segment = ds.sel(
            {"time":
            (ds["datetime"] > start_window) & (ds["datetime"] < end_window)})
        
        for i in ds_segment["time"]:
            ds_point = ds_segment.sel({"time": i})
            dt = (ds_point["datetime"].values - date).days * 24 + \
                (ds_point["datetime"].values - date).seconds / 3600
            print(
                "found DAWN scan at", ds_point["datetime"].values, "dt =", dt)
            current_time = pd.to_datetime(ds_point["datetime"].values)
            if (
                # RF06 parking garage
                ((current_time > datetime(2022, 9, 15, 17, 5)) &
                 (current_time < datetime(2022, 9, 15, 17, 6))) |
                # RF06 racetrack
                ((current_time > datetime(2022, 9, 15, 19, 7)) &
                 (current_time < datetime(2022, 9, 15, 19, 8))) |

                # RF07
                ((current_time > datetime(2022, 9, 16, 20, 10)) &
                 (current_time < datetime(2022, 9, 16, 20, 11))) |

                # RF09 staircase
                ((current_time > datetime(2022, 9, 22, 10, 37, 30)) &
                 (current_time < datetime(2022, 9, 22, 11))) |
                ((current_time > datetime(2022, 9, 22, 11, 18, 30)) &
                 (current_time < datetime(2022, 9, 22, 11, 58))) |

                # RF10 
                ((current_time > datetime(2022, 9, 23, 12, 33)) &
                 (current_time < datetime(2022, 9, 23, 12, 35))) |
                ((current_time > datetime(2022, 9, 23, 13, 6, )) &
                 (current_time < datetime(2022, 9, 23, 13, 13)))
                ):
                print("skipping flyover")
                continue

            nearest_time = pd.Timestamp(ds_point["datetime"].values).round("1h")
            if nearest_time != previous_time:
                if previous_time != None:
                    subprocess.run(
                        f"rm /tmp/wrfinput_d02_{previous_time:%Y-%m-%d_%H:00:00}",
                        shell=True)
                subprocess.run(
                    f"cp {wrfinput_dir}/wrfinput_d02_{nearest_time:%Y-%m-%d_%H:00:00} /tmp",
                    shell=True)
                ds_wrf = xr.open_dataset(
                    f"/tmp/wrfinput_d02_{nearest_time:%Y-%m-%d_%H:00:00}").squeeze()
                ds_wrf["hgt"] = wrf_calc.height(ds_wrf)
                ds_wrf["prs"] = wrf_calc.pressure(ds_wrf) / 100
                previous_time = nearest_time

            df = pd.DataFrame({
                "ZOB": ds_point["altitude"],
                "UOB": ds_point["U_comp"],
                "VOB": ds_point["V_comp"]})
            df.dropna(subset=["UOB", "VOB"], how="all", inplace=True)
            df.fillna(10e10, inplace=True)
    
            if df.size:
                ds_wrf_point = extra.interp_point(
                    ds_wrf, ds_point["lon"], ds_point["lat"])
                df["POB"] = 1 / np.log(wrf_calc.interpolate_1d(
                    ds_wrf_point["hgt"], np.exp(1 / ds_wrf_point["prs"]),
                    df["ZOB"]))

                df.to_csv(
                    "/tmp/dawn_processed.csv", index=False,
                    columns=["POB", "ZOB", "UOB", "VOB"], header=False)

                for prepbufr_filename in config.dawn_prepbufr_filenames:
                    print("adding data to", prepbufr_filename(date))
                    Path(config.prepbufr_dir(date)).mkdir(parents=True, exist_ok=True)
                    subprocess.run(
                        ["/tmp/prepbufr_encode_upperair_dawn.exe",
                        f"/tmp/prepbufr_{date:%Y%m%d}/{prepbufr_filename(date)}",
                        f"{date:%Y%m%d%H}", f"{ds_point['lon'].values + 360}",
                        f"{ds_point['lat'].values}", f"{dt}",
                        "/tmp/dawn_processed.csv"])

    subprocess.run(f"rm /tmp/{dawn_filename}", shell=True)

if previous_time != None:
    subprocess.run(
        f"rm /tmp/wrfinput_d02_{previous_time:%Y-%m-%d_%H:00:00}", shell=True)
for date in pd.date_range(config.start_date, config.end_date, freq="1d"):
    subprocess.run(
        f"mv /tmp/prepbufr_{date:%Y%m%d}/* {config.prepbufr_dir(date)}",
        shell=True)
subprocess.run("rm /tmp/dawn_processed.csv", shell=True)
