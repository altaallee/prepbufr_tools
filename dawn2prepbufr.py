from datetime import datetime, timedelta
import pandas as pd
import xarray as xr
import subprocess
from pathlib import Path


start_date = datetime(2022, 9, 1, 0)
end_date = datetime(2022, 10, 1, 0)
frequency = timedelta(hours=6)

prepbufr_dir = lambda date: f"prepbufr_files/{date:%Y%m%d%H}/"
prepbufr_filename = lambda date: f"dawn.t{date:%H}z.prepbufr.nr"

dawn_dir = "postprocessed_obs/CPEX-CV/DAWN/"
dawn_filename = ""

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
