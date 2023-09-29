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


subprocess.run("cp prepbufr_encode_upperair_dawn.exe /tmp", shell=True)
subprocess.run("cp -r lib /tmp", shell=True)

for date in pd.date_range(
    config.start_date, config.end_date, freq=config.frequency):
    Path(f"/tmp/prepbufr_{date:%Y%m%d}/").mkdir(parents=True, exist_ok=True)
    for prepbufr_filename in config.dawn_prepbufr_filenames:
        subprocess.run(
            f"cp {config.prepbufr_dir(date)}/{prepbufr_filename(date)} /tmp/prepbufr_{date:%Y%m%d}/",
            shell=True)

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
                # RF01
                ((current_time > datetime(2022, 9, 6, 16, 43)) &
                 (current_time < datetime(2022, 9, 6, 16, 47))) |
                ((current_time > datetime(2022, 9, 6, 17, 8)) &
                 (current_time < datetime(2022, 9, 6, 17, 9))) |
                ((current_time > datetime(2022, 9, 6, 17, 14)) &
                 (current_time < datetime(2022, 9, 6, 17, 20))) |

                # RF03 racetrack
                ((current_time > datetime(2022, 9, 9, 14, 14)) &
                 (current_time < datetime(2022, 9, 9, 14, 26))) |
                ((current_time > datetime(2022, 9, 9, 14, 32)) &
                 (current_time < datetime(2022, 9, 9, 14, 34))) |
                # RF03 intersections
                ((current_time > datetime(2022, 9, 9, 16, 59, 30)) &
                 (current_time < datetime(2022, 9, 9, 17, 0, 30))) |
                ((current_time > datetime(2022, 9, 9, 17, 33)) &
                 (current_time < datetime(2022, 9, 9, 17, 36))) |
                ((current_time > datetime(2022, 9, 9, 19, 20, 30)) &
                 (current_time < datetime(2022, 9, 9, 19, 21, 30))) |

                # RF04
                ((current_time > datetime(2022, 9, 10, 16, 23)) &
                 (current_time < datetime(2022, 9, 10, 16, 25))) |
                ((current_time > datetime(2022, 9, 10, 16, 34)) &
                 (current_time < datetime(2022, 9, 10, 16, 36))) |
                ((current_time > datetime(2022, 9, 10, 17, 10, 30)) &
                 (current_time < datetime(2022, 9, 10, 17, 11, 30))) |
                ((current_time > datetime(2022, 9, 10, 17, 18)) &
                 (current_time < datetime(2022, 9, 10, 17, 19))) |
                ((current_time > datetime(2022, 9, 10, 17, 29)) &
                 (current_time < datetime(2022, 9, 10, 17, 31))) |
                ((current_time > datetime(2022, 9, 10, 17, 57)) &
                 (current_time < datetime(2022, 9, 10, 17, 58))) |
                ((current_time > datetime(2022, 9, 10, 18, 24)) &
                 (current_time < datetime(2022, 9, 10, 18, 28))) |
                ((current_time > datetime(2022, 9, 10, 18, 41, 30)) &
                 (current_time < datetime(2022, 9, 10, 18, 42, 30))) |

                # RF05
                ((current_time > datetime(2022, 9, 14, 11, 12)) &
                 (current_time < datetime(2022, 9, 14, 11, 22))) |
                ((current_time > datetime(2022, 9, 14, 14, 44)) &
                 (current_time < datetime(2022, 9, 14, 14, 46))) |

                # RF06 intersection
                ((current_time > datetime(2022, 9, 15, 15, 50)) &
                 (current_time < datetime(2022, 9, 15, 15, 53))) |
                # RF06 parking garage
                ((current_time > datetime(2022, 9, 15, 16, 53)) &
                 (current_time < datetime(2022, 9, 15, 16, 54))) |
                ((current_time > datetime(2022, 9, 15, 17, 5)) &
                 (current_time < datetime(2022, 9, 15, 17, 7))) |
                ((current_time > datetime(2022, 9, 15, 17, 11)) &
                 (current_time < datetime(2022, 9, 15, 17, 14))) |
                ((current_time > datetime(2022, 9, 15, 17, 27)) &
                 (current_time < datetime(2022, 9, 15, 17, 28))) |
                # RF06 racetrack
                ((current_time > datetime(2022, 9, 15, 19, 5)) &
                 (current_time < datetime(2022, 9, 15, 19, 8))) |

                # RF07
                ((current_time > datetime(2022, 9, 16, 16, 3, 30)) &
                 (current_time < datetime(2022, 9, 16, 16, 4, 30))) |
                ((current_time > datetime(2022, 9, 16, 16, 34)) &
                 (current_time < datetime(2022, 9, 16, 16, 36))) |
                ((current_time > datetime(2022, 9, 16, 17, 0)) &
                 (current_time < datetime(2022, 9, 16, 17, 3))) |
                ((current_time > datetime(2022, 9, 16, 17, 11, 30)) &
                 (current_time < datetime(2022, 9, 16, 17, 12, 30))) |
                ((current_time > datetime(2022, 9, 16, 17, 45)) &
                 (current_time < datetime(2022, 9, 16, 17, 47))) |
                ((current_time > datetime(2022, 9, 16, 17, 59)) &
                 (current_time < datetime(2022, 9, 16, 18, 0))) |
                ((current_time > datetime(2022, 9, 16, 20, 4)) &
                 (current_time < datetime(2022, 9, 16, 20, 20))) |

                # RF08
                ((current_time > datetime(2022, 9, 20, 7, 49)) &
                 (current_time < datetime(2022, 9, 20, 7, 51))) |
                ((current_time > datetime(2022, 9, 20, 8, 11, 30)) &
                 (current_time < datetime(2022, 9, 20, 8, 13, 30))) |

                # RF09 intersection
                ((current_time > datetime(2022, 9, 22, 7, 23)) &
                 (current_time < datetime(2022, 9, 22, 7, 24))) |
                ((current_time > datetime(2022, 9, 22, 7, 53, 30)) &
                 (current_time < datetime(2022, 9, 22, 7, 55, 30))) |
                # RF09 staircase
                ((current_time > datetime(2022, 9, 22, 10, 37, 30)) &
                 (current_time < datetime(2022, 9, 22, 11, 0))) |
                ((current_time > datetime(2022, 9, 22, 11, 11)) &
                 (current_time < datetime(2022, 9, 22, 11, 58))) |
                # RF09 intersection
                ((current_time > datetime(2022, 9, 22, 12, 2)) &
                 (current_time < datetime(2022, 9, 22, 12, 5))) |
                ((current_time > datetime(2022, 9, 22, 12, 12, 30)) &
                 (current_time < datetime(2022, 9, 22, 12, 13, 30))) |

                # RF10 
                ((current_time > datetime(2022, 9, 23, 10, 0)) &
                 (current_time < datetime(2022, 9, 23, 10, 1))) |
                ((current_time > datetime(2022, 9, 23, 10, 9)) &
                 (current_time < datetime(2022, 9, 23, 10, 17))) |
                ((current_time > datetime(2022, 9, 23, 11, 25)) &
                 (current_time < datetime(2022, 9, 23, 11, 27))) |
                ((current_time > datetime(2022, 9, 23, 12, 33)) &
                 (current_time < datetime(2022, 9, 23, 12, 35))) |
                ((current_time > datetime(2022, 9, 23, 13, 3)) &
                 (current_time < datetime(2022, 9, 23, 13, 13))) |
                ((current_time > datetime(2022, 9, 23, 13, 16)) &
                 (current_time < datetime(2022, 9, 23, 13, 17))) |
                ((current_time > datetime(2022, 9, 23, 13, 32)) &
                 (current_time < datetime(2022, 9, 23, 13, 33))) |
                ((current_time > datetime(2022, 9, 23, 13, 53)) &
                 (current_time < datetime(2022, 9, 23, 13, 55))) |

                # RF11
                ((current_time > datetime(2022, 9, 26, 8, 26, 30)) &
                 (current_time < datetime(2022, 9, 26, 8, 27, 30))) |
                ((current_time > datetime(2022, 9, 26, 9, 10)) &
                 (current_time < datetime(2022, 9, 26, 9, 11))) |
                ((current_time > datetime(2022, 9, 26, 9, 24)) &
                 (current_time < datetime(2022, 9, 26, 9, 25))) |
                ((current_time > datetime(2022, 9, 26, 9, 34)) &
                 (current_time < datetime(2022, 9, 26, 9, 36))) |
                ((current_time > datetime(2022, 9, 26, 9, 48)) &
                 (current_time < datetime(2022, 9, 26, 9, 52))) |
                ((current_time > datetime(2022, 9, 26, 10, 10)) &
                 (current_time < datetime(2022, 9, 26, 10, 11))) |

                # RF12
                ((current_time > datetime(2022, 9, 29, 7, 44)) &
                 (current_time < datetime(2022, 9, 29, 7, 46))) |
                ((current_time > datetime(2022, 9, 29, 7, 49)) &
                 (current_time < datetime(2022, 9, 29, 7, 50))) |
                ((current_time > datetime(2022, 9, 29, 13, 5, 30)) &
                 (current_time < datetime(2022, 9, 29, 13, 7, 50))) |
                ((current_time > datetime(2022, 9, 29, 13, 18, 30)) &
                 (current_time < datetime(2022, 9, 29, 13, 20)))
                ):
                print("skipping flyover")
                continue

            df = pd.DataFrame({
                "POB": ds_point["prs"],
                "ZOB": ds_point["altitude"],
                "UOB": ds_point["U_comp"],
                "VOB": ds_point["V_comp"]})
            if "UOB" in config.deny_variables:
                df = df.assign(UOB=np.nan)
            if "VOB" in config.deny_variables:
                df = df.assign(VOB=np.nan)
            df.dropna(subset=["UOB", "VOB"], how="all", inplace=True)
            df.fillna(10e10, inplace=True)
    
            if df.size:
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

for date in pd.date_range(config.start_date, config.end_date, freq="1d"):
    subprocess.run(
        f"mv /tmp/prepbufr_{date:%Y%m%d}/* {config.prepbufr_dir(date)}",
        shell=True)
    subprocess.run(f"rm -rf /tmp/prepbufr_{date:%Y%m%d}", shell=True)
subprocess.run("rm /tmp/dawn_processed.csv", shell=True)
subprocess.run("rm -rf /tmp/lib", shell=True)
subprocess.run("rm /tmp/prepbufr_encode_upperair_dawn.exe", shell=True)
