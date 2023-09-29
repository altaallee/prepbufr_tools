import config
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


subprocess.run("cp prepbufr_encode_upperair_halo.exe /tmp", shell=True)
subprocess.run("cp -r lib /tmp", shell=True)

for date in pd.date_range(
    config.start_date, config.end_date, freq=config.frequency):
    Path(f"/tmp/prepbufr_{date:%Y%m%d}/").mkdir(parents=True, exist_ok=True)
    for prepbufr_filename in config.halo_prepbufr_filenames:
        subprocess.run(
            f"cp {config.prepbufr_dir(date)}/{prepbufr_filename(date)} /tmp/prepbufr_{date:%Y%m%d}/",
            shell=True)

for halo_filename in config.halo_filenames:
    subprocess.run(f"cp {config.halo_data_dir}/{halo_filename} /tmp", shell=True)
    ds = xr.load_dataset(f"/tmp/{halo_filename}")
    ds = ds.sel({"time": ds["time"][::config.skip]})

    ds["Specific_Humidity"] = mpcalc.specific_humidity_from_mixing_ratio(
        ds["h2o_mmr_v"] * units("gram / kilogram")).metpy.convert_units("milligrams / kilogram")

    for date in pd.date_range(
        config.start_date, config.end_date, freq=config.frequency):
        print("creating prepbufr for", date)

        start_window = date - config.frequency / 2
        end_window = date + config.frequency / 2
        print("searching for HALO data between", start_window, end_window)

        ds_segment = ds.sel(
            {"time": (ds["datetime"] > start_window) & (ds["datetime"] < end_window)})
        
        for i in ds_segment["time"]:
            ds_point = ds_segment.sel({"time": i})
            dt = (ds_point["datetime"].values - date).days * 24 + \
                (ds_point["datetime"].values - date).seconds / 3600
            print("found HALO scan at", ds_point["datetime"].values, "dt =", dt)
            current_time = pd.to_datetime(ds_point["datetime"].values)
            if (
                # RF03 sprial
                ((current_time > datetime(2022, 9, 9, 12, 57)) &
                 (current_time < datetime(2022, 9, 9, 13, 2))) |
                ((current_time > datetime(2022, 9, 9, 13, 6)) &
                 (current_time < datetime(2022, 9, 9, 13, 7))) |
                ((current_time > datetime(2022, 9, 9, 14, 14)) &
                 (current_time < datetime(2022, 9, 9, 14, 16))) |
                # RF03 intersections
                ((current_time > datetime(2022, 9, 9, 17, 43)) &
                 (current_time < datetime(2022, 9, 9, 17, 45))) |
                ((current_time > datetime(2022, 9, 9, 19, 12)) &
                 (current_time < datetime(2022, 9, 9, 19, 15, 30))) |
                ((current_time > datetime(2022, 9, 9, 19, 20)) &
                 (current_time < datetime(2022, 9, 9, 19, 21, 30))) |

                # RF04 spiral
                ((current_time > datetime(2022, 9, 10, 16, 15)) &
                 (current_time < datetime(2022, 9, 10, 16, 19))) |
                # RF04 figure 4
                ((current_time > datetime(2022, 9, 10, 17, 18)) &
                 (current_time < datetime(2022, 9, 10, 17, 19, 30))) |
                # RF04 racetrack
                ((current_time > datetime(2022, 9, 10, 18, 7)) &
                 (current_time < datetime(2022, 9, 10, 18, 9))) |
                ((current_time > datetime(2022, 9, 10, 18, 19)) &
                 (current_time < datetime(2022, 9, 10, 18, 28))) |
                # RF04 loop
                ((current_time > datetime(2022, 9, 10, 18, 34)) &
                 (current_time < datetime(2022, 9, 10, 18, 35))) |
                ((current_time > datetime(2022, 9, 10, 18, 37)) &
                 (current_time < datetime(2022, 9, 10, 18, 39))) |
                ((current_time > datetime(2022, 9, 10, 18, 41)) &
                 (current_time < datetime(2022, 9, 10, 18, 43))) |

                # RF06 intersection
                ((current_time > datetime(2022, 9, 15, 15, 50)) &
                 (current_time < datetime(2022, 9, 15, 15, 53))) |
                # RF06 parking garage
                ((current_time > datetime(2022, 9, 15, 17, 30)) &
                 (current_time < datetime(2022, 9, 15, 17, 32))) |
                # RF06 racetrack
                ((current_time > datetime(2022, 9, 15, 18, 49, 30)) &
                 (current_time < datetime(2022, 9, 15, 18, 50, 30))) |
                ((current_time > datetime(2022, 9, 15, 19, 1)) &
                 (current_time < datetime(2022, 9, 15, 19, 8))) |

                # RF07
                ((current_time > datetime(2022, 9, 16, 15, 52)) &
                 (current_time < datetime(2022, 9, 16, 15, 53))) |
                ((current_time > datetime(2022, 9, 16, 16, 4)) &
                 (current_time < datetime(2022, 9, 16, 16, 5))) |
                ((current_time > datetime(2022, 9, 16, 16, 50, 30)) &
                 (current_time < datetime(2022, 9, 16, 16, 51, 30))) |
                ((current_time > datetime(2022, 9, 16, 17, 0)) &
                 (current_time < datetime(2022, 9, 16, 17, 3))) |
                ((current_time > datetime(2022, 9, 16, 18, 1)) &
                 (current_time < datetime(2022, 9, 16, 18, 2))) |

                # RF08 intersections
                ((current_time > datetime(2022, 9, 20, 6, 2)) &
                 (current_time < datetime(2022, 9, 20, 6, 3))) |
                ((current_time > datetime(2022, 9, 20, 7, 48, 30)) &
                 (current_time < datetime(2022, 9, 20, 7, 50, 30))) |

                # RF09 staircase
                ((current_time > datetime(2022, 9, 22, 10, 39)) &
                 (current_time < datetime(2022, 9, 22, 10, 44))) |
                ((current_time > datetime(2022, 9, 22, 10, 46)) &
                 (current_time < datetime(2022, 9, 22, 11, 1))) |
                ((current_time > datetime(2022, 9, 22, 11, 16)) &
                 (current_time < datetime(2022, 9, 22, 11, 58))) |

                # RF10 spiral
                ((current_time > datetime(2022, 9, 23, 7, 10)) &
                 (current_time < datetime(2022, 9, 23, 7, 32))) |
                ((current_time > datetime(2022, 9, 23, 7, 33)) &
                 (current_time < datetime(2022, 9, 23, 7, 43))) |
                ((current_time > datetime(2022, 9, 23, 7, 44)) &
                 (current_time < datetime(2022, 9, 23, 7, 49, 30))) |
                # RF10 bottom overlap
                ((current_time > datetime(2022, 9, 23, 9, 59, 30)) &
                 (current_time < datetime(2022, 9, 23, 10, 2))) |
                ((current_time > datetime(2022, 9, 23, 10, 6)) &
                 (current_time < datetime(2022, 9, 23, 10, 12))) |
                # RF10 intersections
                ((current_time > datetime(2022, 9, 23, 11, 32, 30)) &
                 (current_time < datetime(2022, 9, 23, 11, 33, 30))) |
                ((current_time > datetime(2022, 9, 23, 13, 59)) &
                 (current_time < datetime(2022, 9, 23, 14, 0))) |

                # RF12
                ((current_time > datetime(2022, 9, 29, 7, 44)) &
                 (current_time < datetime(2022, 9, 29, 7, 47))) |
                ((current_time > datetime(2022, 9, 29, 7, 48)) &
                 (current_time < datetime(2022, 9, 29, 7, 50)))
                ):
                print("skipping flyover")
                continue

            df = pd.DataFrame({
                "POB": ds_point["prs"],
                "QOB": ds_point["Specific_Humidity"],
                "ZOB": ds_point["altitude"]})
            if "QOB" in config.deny_variables:
                df = df.assign(QOB=np.nan)
            df.dropna(subset=["QOB"], inplace=True)
            df.fillna(10e10, inplace=True)
    
            if df.size:
                df.to_csv("/tmp/halo_processed.csv", index=False,
                    columns=["POB", "QOB", "ZOB"], header=False)

                for prepbufr_filename in config.halo_prepbufr_filenames:
                    print("adding data to", prepbufr_filename(date))
                    Path(config.prepbufr_dir(date)).mkdir(
                        parents=True, exist_ok=True)
                    subprocess.run(
                        ["/tmp/prepbufr_encode_upperair_halo.exe",
                        f"/tmp/prepbufr_{date:%Y%m%d}/{prepbufr_filename(date)}",
                        f"{date:%Y%m%d%H}", f"{ds_point['lon'].values + 360}",
                        f"{ds_point['lat'].values}", f"{dt}",
                        "/tmp/halo_processed.csv"])
    subprocess.run(f"rm /tmp/{halo_filename}", shell=True)

for date in pd.date_range(config.start_date, config.end_date, freq="1d"):
    subprocess.run(
        f"mv /tmp/prepbufr_{date:%Y%m%d}/* {config.prepbufr_dir(date)}",
        shell=True)
    subprocess.run(f"rm -rf /tmp/prepbufr_{date:%Y%m%d}", shell=True)
subprocess.run("rm /tmp/halo_processed.csv", shell=True)
subprocess.run("rm -rf /tmp/lib", shell=True)
subprocess.run("rm /tmp/prepbufr_encode_upperair_halo.exe", shell=True)
