import sys
sys.path.insert(1, "../plotters_cv")
from python_imports import config
from datetime import datetime, timedelta
import glob
import xarray as xr
import pandas as pd
import numpy as np
import multiprocessing as mp
import subprocess
from pathlib import Path


output_path = "postprocessed_overlapping_obs/CPEX-CV/DAWN/"
file_path = "postprocessed_obs/CPEX-CV/DAWN/with_pressure/45_model_levels/"
flight_segments = [
    {"filename": "cpexcv-DAWN_DC8_20220922_R0.nc_full_averaged_12000.nc",
     "start": datetime(2022, 9, 22, 10, 3),
     "end": datetime(2022, 9, 22, 12, 5)}
]

#output_path = "postprocessed_overlapping_obs/CPEX-CV/HALO/"
#file_path = "postprocessed_obs/CPEX-CV/HALO/with_pressure/45_model_levels_pqc/"
#flight_segments = [
#    {"filename": "CPEXCV-HALO_DC8_20220922_R1.h5_full_averaged_12000.nc",
#     "start": datetime(2022, 9, 22, 10, 3),
#     "end": datetime(2022, 9, 22, 12, 0)}
#]

#output_path = "postprocessed_overlapping_obs/CPEX-CV/HAMSR/"
#file_path = "postprocessed_obs/CPEX-CV/HAMSR/45_model_levels/"
#flight_segments = [
#    {"filename": "CPEXCV-HAMSR-data_DC8_20220922_nadir.nc_full_averaged_12000_combined.nc",
#     "start": datetime(2022, 9, 22, 10, 3),
#     "end": datetime(2022, 9, 22, 12, 5)}
#]

Path(output_path).mkdir(parents=True, exist_ok=True)

def get_average_profile(i):
    blonL = df_wrfgrids["lonL"][i]
    blonR = df_wrfgrids["lonR"][i]
    blatS = df_wrfgrids["latS"][i]
    blatN = df_wrfgrids["latN"][i]
    ds_grid = ds_subdata.sel(
        {"time": 
         (ds_subdata["lon"] >= blonL) & (ds_subdata["lon"] < blonR) &
         (ds_subdata["lat"] >= blatS) & (ds_subdata["lat"] < blatN)}, drop=True)
        return ds_grid.mean("time", skipna=True)
    return

def multicore(number):
    with mp.Pool(maxtasksperchild=1) as pool:
        profile_values = pool.map_async(get_average_profile, range(number))
        curtain = profile_values.get()
        pool.close()
        pool.join()
    return list(filter(lambda item: item is not None, curtain))

if __name__ == "__main__":
    ds_wrf = xr.open_dataset(
        glob.glob(f"../plotters_cv/data/{config.wrf_dir}/{config.wrf_subdir}/wrfout_d01_*")[0]).squeeze()
    ny, nx = ds_wrf["XLONG"].shape

    global df_wrfgrids
    df_wrfgrids = pd.DataFrame(
        {"lonL": ds_wrf["XLONG_U"].isel(
             {"south_north": slice(0, ny), "west_east_stag": slice(0, nx)}).stack(
                 n=["south_north", "west_east_stag"]).values,
         "lonR": ds_wrf["XLONG_U"].isel(
             {"south_north": slice(0, ny), "west_east_stag": slice(1, nx + 1)}).stack(
                 n=["south_north", "west_east_stag"]).values,
         "latS": ds_wrf["XLAT_V"].isel(
             {"south_north_stag": slice(0, ny), "west_east": slice(0, nx)})[0:ny, 0:nx].stack(
                 n=["south_north_stag", "west_east"]).values,
         "latN": ds_wrf["XLAT_V"].isel(
             {"south_north_stag": slice(1, ny + 1), "west_east": slice(0, nx)}).stack(
                 n=["south_north_stag", "west_east"]).values})
    df_wrfgrids_with_index = df_wrfgrids.rename_axis("grid_idx").reset_index()

    for flight_segment in flight_segments:
        subprocess.run(
            f"cp {file_path}/{flight_segment['filename']} /tmp", shell=True)
        ds_data = xr.open_dataset(f"/tmp/{flight_segment['filename']}")
        global ds_subdata
        ds_subdata = ds_data.sel(
            {"time": (pd.to_datetime(ds_data["datetime"]) > flight_segment["start"]) &
                     (pd.to_datetime(ds_data["datetime"]) < flight_segment["end"])})

        curtain = multicore(nx * ny)
        averaged = xr.concat(curtain, dim="time")
        averaged["altitude"] = ds_data["altitude"]
        averaged["datetime"] = xr.DataArray(
            pd.to_datetime(
                [datetime(1970, 1, 1) + timedelta(seconds=seconds) for seconds
                 in averaged["dt_float"].values]),
            dims=["time"])
        averaged["time"] = np.arange(len(averaged["time"]))

        averaged.to_netcdf(
            f"{output_path}/{flight_segment['filename']}_overlap_{flight_segment['start']:%Y%m%d%H%M}_{flight_segment['end']:%Y%m%d%H%M}.nc")
