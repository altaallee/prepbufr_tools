import sys
sys.path.insert(1, "../dev/plotters/")
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

prepbufr_dir = lambda date: f"../CPEX-CV/GDAS3/{date:%Y%m%d}/"
prepbufr_filenames = [
    lambda date: f"gdas_halo.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_dropsonde_halo.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_halo.t{date:%H}z.prepbufr.nr",
    lambda date: f"halo.t{date:%H}z.prepbufr.nr",
]

halo_dir = "postprocessed_obs/CPEX-CV/HALO/"
halo_filenames = [
    "cpexcv-HALO_DC8_20220906_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220907_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220909_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220910_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220914_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220915_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220916_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220920_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220922_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220923_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220926_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220929_RA.h5_full_averaged_12000.nc",
    "cpexcv-HALO_DC8_20220930_RA.h5_full_averaged_12000.nc",
]

wrfinput_dir = "/nobackupp12/alee31/CPEX-CV/era5_wrfinput/"

previous_time = None
for halo_filename in halo_filenames:
    ds = xr.load_dataset(f"{halo_dir}/{halo_filename}")

    ds["Specific_Humidity"] = mpcalc.specific_humidity_from_mixing_ratio(
        ds["h2o_mmr_v"] * units("gram / kilogram")).metpy.convert_units("milligrams / kilogram")

    # ds["datetime"] = xr.DataArray([date + timedelta(days=1) for date in pd.to_datetime(ds["datetime"])], coords={"x": ds.x})
    for date in pd.date_range(start_date, end_date, freq=frequency):
        print("creating prepbufr for", date)

        start_window = date - frequency / 2
        end_window = date + frequency / 2
        print("searching for HALO data between", start_window, end_window)

        ds_segment = ds.sel(
            {"x": (ds["datetime"] > start_window) & (ds["datetime"] < end_window)})
        
        for i in ds_segment["x"]:
            ds_point = ds_segment.sel({"x": i})
            dt = (ds_point["datetime"].values - date).days * 24 + \
                (ds_point["datetime"].values - date).seconds / 3600
            print("found HALO scan at", ds_point["datetime"].values, "dt =", dt)

            nearest_time = pd.Timestamp(ds_point["datetime"].values).round("1h")
            if nearest_time != previous_time:
                ds_wrf = xr.open_dataset(
                    f"{wrfinput_dir}/wrfinput_d02_{nearest_time:%Y-%m-%d_%H:00:00}").squeeze()
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
                df.to_csv("halo_processed.csv", index=False,
                    columns=["POB", "QOB", "ZOB"], header=False)

                for prepbufr_filename in prepbufr_filenames:
                    print("adding data to", prepbufr_filename(date))
                    Path(prepbufr_dir(date)).mkdir(parents=True, exist_ok=True)
                    subprocess.run(
                        ["./prepbufr_encode_upperair_halo.exe",
                        f"{prepbufr_dir(date)}/{prepbufr_filename(date)}",
                        f"{date:%Y%m%d%H}", f"{ds_point['lon'].values + 360}",
                        f"{ds_point['lat'].values}", f"{dt}",
                        "halo_processed.csv"])
