from datetime import datetime, timedelta
import pandas as pd
import xarray as xr
import subprocess
from pathlib import Path


start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 28, 18)
frequency = timedelta(hours=6)

prepbufr_dir = lambda date: f"../CPEX-CV/GDAS/{date:%Y%m%d}/"
prepbufr_filename = lambda date: f"gdas_dawn.t{date:%H}z.prepbufr.nr"
prepbufr_filename = lambda date: f"gdas_dawn_dropsonde_halo.t{date:%H}z.prepbufr.nr"
prepbufr_filename = lambda date: f"gdas_dawn_halo.t{date:%H}z.prepbufr.nr"
prepbufr_filename = lambda date: f"dawn_halo.t{date:%H}z.prepbufr.nr"

dawn_dir = "postprocessed_obs/CPEX-CV/DAWN/"
dawn_filenames = [
    "cpexcv-DAWN_DC8_20220906_RA_RF01.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220907_RA_RF02.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220909_RA_RF03.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220910_RA_RF04.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220914_RA_RF05.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220915_RA_RF06.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220916_RA_RF07.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220920_RA_RF08.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220922_RA_RF09.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220923_RA_RF10.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220926_RA_RF11.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220929_RA_RF12.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220930_RA_RF13.nc_full_averaged_12000.nc"
]

for dawn_filename in dawn_filenames:
    ds = xr.load_dataset(f"{dawn_dir}/{dawn_filename}")

    for date in pd.date_range(start_date, end_date, freq=frequency):
        print("creating prepbufr for", date)

        start_window = date - frequency / 2
        end_window = date + frequency / 2
        print("searching for DAWN data between", start_window, end_window)

        ds_segment = ds.sel(
            {"number_profile_records":
            (ds["datetime"] > start_window) & (ds["datetime"] < end_window)})
        
        for i in ds_segment["number_profile_records"]:
            ds_point = ds_segment.sel({"number_profile_records": i})
            dt = (ds_point["datetime"].values - date).days * 24 + \
                (ds_point["datetime"].values - date).seconds / 3600
            print("found DAWN scan at", ds_point["datetime"].values, "dt =", dt)
            df = pd.DataFrame({
                "ZOB": ds_point["altitude"],
                "UOB": ds_point["U_comp"],
                "VOB": ds_point["V_comp"]})
            df.dropna(subset=["UOB", "VOB"], how="all", inplace=True)
            df.fillna(10e10, inplace=True)
    
            if df.size:
                df.to_csv("dawn_processed.csv", index=False, header=False)

                print("adding data to", prepbufr_filename(date))
                Path(prepbufr_dir(date)).mkdir(parents=True, exist_ok=True)
                subprocess.run(
                    ["./prepbufr_encode_upperair_dawn.exe",
                    f"{prepbufr_dir(date)}/{prepbufr_filename(date)}",
                    f"{date:%Y%m%d%H}",
                    f"{ds_point['Profile_Longitude'].values + 360}",
                    f"{ds_point['Profile_Latitude'].values}", f"{dt}",
                    "dawn_processed.csv"])
