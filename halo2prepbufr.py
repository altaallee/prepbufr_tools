import sys
sys.path.insert(1, "../plotters_cv/")
from datetime import datetime, timedelta
import xarray as xr
from python_imports import extra, wrf_calc
import metpy.calc as mpcalc
from metpy.units import units
import pandas as pd
import numpy as np
from pathlib import Path
import subprocess


start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 30, 18)
frequency = timedelta(hours=6)

prepbufr_dir = lambda date: f"../CPEX-CV/GDAS_R0_HALO_R1/{date:%Y%m%d}/"
prepbufr_filenames = [
    lambda date: f"gdas_halo.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_dropsonde_halo.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_halo.t{date:%H}z.prepbufr.nr",
    lambda date: f"halo.t{date:%H}z.prepbufr.nr",
]

halo_dir = "postprocessed_obs/CPEX-CV/HALO/"
halo_filenames = [
    "CPEXCV-HALO_DC8_20220903_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220906_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220907_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220909_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220910_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220914_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220915_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220916_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220920_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220922_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220923_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220926_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220929_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220930_R1.h5_full_averaged_12000.nc",
]

wrfinput_dir = "/nobackupp28/alee31/CPEX-CV/era5_wrfinput/"

subprocess.run("cp prepbufr_encode_upperair_halo.exe /tmp", shell=True)
subprocess.run("cp -r lib /tmp", shell=True)

for date in pd.date_range(start_date, end_date, freq=frequency):
    Path(f"/tmp/prepbufr_{date:%Y%m%d}/").mkdir(parents=True, exist_ok=True)
    for prepbufr_filename in prepbufr_filenames:
        subprocess.run(
            f"cp {prepbufr_dir(date)}/{prepbufr_filename(date)} /tmp/prepbufr_{date:%Y%m%d}/",
            shell=True)

previous_time = None
for halo_filename in halo_filenames:
    subprocess.run(f"cp {halo_dir}/{halo_filename} /tmp", shell=True)
    ds = xr.load_dataset(f"/tmp/{halo_filename}")

    ds["Specific_Humidity"] = mpcalc.specific_humidity_from_mixing_ratio(
        ds["h2o_mmr_v"] * units("gram / kilogram")).metpy.convert_units("milligrams / kilogram")

    # ds["datetime"] = xr.DataArray([date + timedelta(days=1) for date in pd.to_datetime(ds["datetime"])], coords={"x": ds.x})
    for date in pd.date_range(start_date, end_date, freq=frequency):
        print("creating prepbufr for", date)

        start_window = date - frequency / 2
        end_window = date + frequency / 2
        print("searching for HALO data between", start_window, end_window)

        ds_segment = ds.sel(
            {"time": (ds["datetime"] > start_window) & (ds["datetime"] < end_window)})
        
        for i in ds_segment["time"]:
            ds_point = ds_segment.sel({"time": i})
            dt = (ds_point["datetime"].values - date).days * 24 + \
                (ds_point["datetime"].values - date).seconds / 3600
            print("found HALO scan at", ds_point["datetime"].values, "dt =", dt)
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
                "QOB": ds_point["Specific_Humidity"],
                "ZOB": ds_point["altitude"]})
            df.dropna(subset=["QOB"], inplace=True)
            df.fillna(10e10, inplace=True)
    
            if df.size:
                ds_wrf_point = extra.interp_point(
                    ds_wrf, ds_point["lon"], ds_point["lat"])
                df["POB"] = 1 / np.log(wrf_calc.interpolate_1d(
                    ds_wrf_point["hgt"], np.exp(1 / ds_wrf_point["prs"]),
                    df["ZOB"]))
                df.to_csv("/tmp/halo_processed.csv", index=False,
                    columns=["POB", "QOB", "ZOB"], header=False)

                for prepbufr_filename in prepbufr_filenames:
                    print("adding data to", prepbufr_filename(date))
                    Path(prepbufr_dir(date)).mkdir(parents=True, exist_ok=True)
                    subprocess.run(
                        ["/tmp/prepbufr_encode_upperair_halo.exe",
                        f"/tmp/prepbufr_{date:%Y%m%d}/{prepbufr_filename(date)}",
                        f"{date:%Y%m%d%H}", f"{ds_point['lon'].values + 360}",
                        f"{ds_point['lat'].values}", f"{dt}",
                        "/tmp/halo_processed.csv"])
    subprocess.run(f"rm /tmp/{halo_filename}", shell=True)

if previous_time != None:
    subprocess.run(
        f"rm /tmp/wrfinput_d02_{previous_time:%Y-%m-%d_%H:00:00}", shell=True)
for date in pd.date_range(start_date, end_date, freq="1d"):
    subprocess.run(
        f"mv /tmp/prepbufr_{date:%Y%m%d}/* {prepbufr_dir(date)}", shell=True)
subprocess.run("rm /tmp/halo_processed.csv", shell=True)
