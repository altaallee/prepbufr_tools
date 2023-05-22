import sys
sys.path.insert(1, "../plotters_cv/")
from datetime import datetime, timedelta
import pandas as pd
import xarray as xr
from python_imports import extra, wrf_calc
import numpy as np
import subprocess
from pathlib import Path


start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 30, 18)
frequency = timedelta(hours=6)

prepbufr_dir = lambda date: f"../CPEX-CV/GDAS/{date:%Y%m%d}/"
prepbufr_filenames = [
    lambda date: f"gdas_dawn.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_dropsonde_halo.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_halo.t{date:%H}z.prepbufr.nr",
    lambda date: f"dawn.t{date:%H}z.prepbufr.nr",
]

dawn_dir = "postprocessed_obs/CPEX-CV/DAWN/"
dawn_filenames = [
]

wrfinput_dir = "/nobackupp28/alee31/CPEX-CV/era5_wrfinput/"

subprocess.run("cp prepbufr_encode_upperair_dawn.exe /tmp", shell=True)
subprocess.run("cp -r lib /tmp", shell=True)

for date in pd.date_range(start_date, end_date, freq=frequency):
    Path(f"/tmp/prepbufr_{date:%Y%m%d}/").mkdir(parents=True, exist_ok=True)
    for prepbufr_filename in prepbufr_filenames:
        subprocess.run(
            f"cp {prepbufr_dir(date)}/{prepbufr_filename(date)} /tmp/prepbufr_{date:%Y%m%d}/",
            shell=True)

previous_time = None
for dawn_filename in dawn_filenames:
    subprocess.run(f"cp {dawn_dir}/{dawn_filename} /tmp", shell=True)
    ds = xr.load_dataset(f"/tmp/{dawn_filename}")

    for date in pd.date_range(start_date, end_date, freq=frequency):
        print("creating prepbufr for", date)

        start_window = date - frequency / 2
        end_window = date + frequency / 2
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
            if (((current_time > datetime(2022, 9, 22, 10, 30)) &
                 (current_time < datetime(2022, 9, 22, 11, 2))) |
                 ((current_time > datetime(2022, 9, 22, 11, 10)) &
                  (current_time < datetime(2022, 9, 22, 12, 5)))):
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

                for prepbufr_filename in prepbufr_filenames:
                    print("adding data to", prepbufr_filename(date))
                    Path(prepbufr_dir(date)).mkdir(parents=True, exist_ok=True)
                    subprocess.run(
                        ["/tmp/prepbufr_encode_upperair_dawn.exe",
                        f"/tmp/prepbufr_{date:%Y%m%d}/{prepbufr_filename(date)}",
                        f"{date:%Y%m%d%H}", f"{ds_point['lon'].values + 360}",
                        f"{ds_point['lat'].values}", f"{dt}",
                        "/tmp/dawn_processed.csv"])

    subprocess.run(f"rm /tmp/{dawn_filename}", shell=True)

for date in pd.date_range(start_date, end_date, freq="1d"):
    subprocess.run(
        f"mv /tmp/prepbufr_{date:%Y%m%d}/* {prepbufr_dir(date)}", shell=True)
