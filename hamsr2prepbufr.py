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


subprocess.run("cp prepbufr_encode_upperair_hamsr.exe /tmp", shell=True)
subprocess.run("cp -r lib /tmp", shell=True)

for date in pd.date_range(
    config.start_date, config.end_date, freq=config.frequency):
    Path(f"/tmp/prepbufr_{date:%Y%m%d}/").mkdir(parents=True, exist_ok=True)
    for prepbufr_filename in config.hamsr_prepbufr_filenames:
        subprocess.run(
            f"cp {config.prepbufr_dir(date)}/{prepbufr_filename(date)} /tmp/prepbufr_{date:%Y%m%d}/",
            shell=True)

for hamsr_filename in config.hamsr_filenames:
    subprocess.run(f"cp {config.hamsr_data_dir}/{hamsr_filename} /tmp", shell=True)
    ds = xr.load_dataset(f"/tmp/{hamsr_filename}")

    ds["Specific_Humidity"] = mpcalc.specific_humidity_from_mixing_ratio(
        ds["QVAPOR"] * units("gram / kilogram")).metpy.convert_units("milligrams / kilogram")
    ds["Tv"] = mpcalc.virtual_temperature(
        ds["TMP"] * units("kelvin"), ds["QVAPOR"] * units("grams / kilogram")).metpy.convert_units("celsius")

    for date in pd.date_range(
        config.start_date, config.end_date, freq=config.frequency):
        print("creating prepbufr for", date)

        start_window = date - config.frequency / 2
        end_window = date + config.frequency / 2
        print("searching for HAMSR data between", start_window, end_window)

        ds_segment = ds.sel(
            {"time": (ds["datetime"] > start_window) & (ds["datetime"] < end_window)})
        
        for i in ds_segment["time"]:
            ds_point = ds_segment.sel({"time": i})
            dt = (ds_point["datetime"].values - date).days * 24 + \
                (ds_point["datetime"].values - date).seconds / 3600
            print(
                "found HAMSR scan at", ds_point["datetime"].values, "dt =", dt)
            current_time = pd.to_datetime(ds_point["datetime"].values)
            if (
                # RF01
                ((current_time > datetime(2022, 9, 6, 17, 15)) &
                 (current_time < datetime(2022, 9, 6, 17, 18))) |

                # RF03 sprial
                ((current_time > datetime(2022, 9, 9, 12, 45)) &
                 (current_time < datetime(2022, 9, 9, 12, 48, 30))) |
                ((current_time > datetime(2022, 9, 9, 12, 45)) &
                 (current_time < datetime(2022, 9, 9, 13, 2))) |
                ((current_time > datetime(2022, 9, 9, 13, 6)) &
                 (current_time < datetime(2022, 9, 9, 13, 7))) |
                # RF03 Staircase
                ((current_time > datetime(2022, 9, 9, 14, 13)) &
                 (current_time < datetime(2022, 9, 9, 14, 18, 30))) |
                ((current_time > datetime(2022, 9, 9, 14, 33, 30)) &
                 (current_time < datetime(2022, 9, 9, 14, 34, 30))) |
                # RF03 intersections
                ((current_time > datetime(2022, 9, 9, 18, 31, 30)) &
                 (current_time < datetime(2022, 9, 9, 18, 32, 30))) |
                ((current_time > datetime(2022, 9, 9, 18, 57, 30)) &
                 (current_time < datetime(2022, 9, 9, 18, 58, 30))) |
                ((current_time > datetime(2022, 9, 9, 19, 12)) &
                 (current_time < datetime(2022, 9, 9, 19, 16))) |
                ((current_time > datetime(2022, 9, 9, 19, 20)) &
                 (current_time < datetime(2022, 9, 9, 19, 21))) |

                # RF04 spiral
                ((current_time > datetime(2022, 9, 10, 16, 13)) &
                 (current_time < datetime(2022, 9, 10, 16, 14))) |
                ((current_time > datetime(2022, 9, 10, 16, 15)) &
                 (current_time < datetime(2022, 9, 10, 16, 20, 30))) |
                ((current_time > datetime(2022, 9, 10, 16, 23)) &
                 (current_time < datetime(2022, 9, 10, 16, 24))) |
                ((current_time > datetime(2022, 9, 10, 16, 25)) &
                 (current_time < datetime(2022, 9, 10, 16, 27))) |
                # RF04 figure 4
                ((current_time > datetime(2022, 9, 10, 17, 10)) &
                 (current_time < datetime(2022, 9, 10, 17, 14))) |
                ((current_time > datetime(2022, 9, 10, 17, 18, 30)) &
                 (current_time < datetime(2022, 9, 10, 17, 19, 30))) |
                ((current_time > datetime(2022, 9, 10, 17, 29, 30)) &
                 (current_time < datetime(2022, 9, 10, 17, 31, 30))) |
                # RF04 racetrack
                ((current_time > datetime(2022, 9, 10, 18, 18)) &
                 (current_time < datetime(2022, 9, 10, 18, 30))) |
                ((current_time > datetime(2022, 9, 10, 18, 40, 30)) &
                 (current_time < datetime(2022, 9, 10, 18, 43))) |

                # RF05
                ((current_time > datetime(2022, 9, 14, 10, 0)) &
                 (current_time < datetime(2022, 9, 14, 10, 3))) |
                ((current_time > datetime(2022, 9, 14, 13, 40)) &
                 (current_time < datetime(2022, 9, 14, 13, 48))) |
                ((current_time > datetime(2022, 9, 14, 13, 51)) &
                 (current_time < datetime(2022, 9, 14, 13, 53))) |

                # RF06 intersection
                ((current_time > datetime(2022, 9, 15, 15, 51)) &
                 (current_time < datetime(2022, 9, 15, 15, 53))) |
                # RF06 parking garage
                ((current_time > datetime(2022, 9, 15, 16, 50)) &
                 (current_time < datetime(2022, 9, 15, 17, 25))) |
                ((current_time > datetime(2022, 9, 15, 17, 29)) &
                 (current_time < datetime(2022, 9, 15, 17, 32))) |
                # RF06 racetrack
                ((current_time > datetime(2022, 9, 15, 19, 1, 30)) &
                 (current_time < datetime(2022, 9, 15, 19, 9))) |

                # RF07
                ((current_time > datetime(2022, 9, 16, 15, 52)) &
                 (current_time < datetime(2022, 9, 16, 15, 54))) |
                ((current_time > datetime(2022, 9, 16, 16, 3, 30)) &
                 (current_time < datetime(2022, 9, 16, 16, 4, 30))) |
                ((current_time > datetime(2022, 9, 16, 16, 50, 30)) &
                 (current_time < datetime(2022, 9, 16, 16, 51, 30))) |
                ((current_time > datetime(2022, 9, 16, 16, 55, 30)) &
                 (current_time < datetime(2022, 9, 16, 16, 56, 30))) |
                ((current_time > datetime(2022, 9, 16, 16, 57)) &
                 (current_time < datetime(2022, 9, 16, 17, 3))) |
                ((current_time > datetime(2022, 9, 16, 17, 8, 30)) &
                 (current_time < datetime(2022, 9, 16, 17, 10))) |
                ((current_time > datetime(2022, 9, 16, 17, 12)) &
                 (current_time < datetime(2022, 9, 16, 17, 13))) |
                ((current_time > datetime(2022, 9, 16, 17, 59)) &
                 (current_time < datetime(2022, 9, 16, 18, 1))) |
                ((current_time > datetime(2022, 9, 16, 17, 36)) &
                 (current_time < datetime(2022, 9, 16, 17, 37, 30))) |
                ((current_time > datetime(2022, 9, 16, 19, 54, 30)) &
                 (current_time < datetime(2022, 9, 16, 19, 55, 30))) |
                ((current_time > datetime(2022, 9, 16, 19, 57)) &
                 (current_time < datetime(2022, 9, 16, 20, 11))) |

                # RF08 intersections
                ((current_time > datetime(2022, 9, 20, 6, 2)) &
                 (current_time < datetime(2022, 9, 20, 6, 3))) |
                ((current_time > datetime(2022, 9, 20, 6, 14)) &
                 (current_time < datetime(2022, 9, 20, 6, 15))) |

                # RF09 staircase
                ((current_time > datetime(2022, 9, 22, 10, 35)) &
                 (current_time < datetime(2022, 9, 22, 11, 2))) |
                ((current_time > datetime(2022, 9, 22, 11, 10)) &
                 (current_time < datetime(2022, 9, 22, 11, 31))) |
                ((current_time > datetime(2022, 9, 22, 11, 34)) &
                 (current_time < datetime(2022, 9, 22, 11, 45))) |
                ((current_time > datetime(2022, 9, 22, 11, 47)) &
                 (current_time < datetime(2022, 9, 22, 11, 58))) |
                ((current_time > datetime(2022, 9, 22, 12, 1)) &
                 (current_time < datetime(2022, 9, 22, 12, 5))) |
                ((current_time > datetime(2022, 9, 22, 12, 12)) &
                 (current_time < datetime(2022, 9, 22, 12, 15))) |

                # RF10 spiral
                ((current_time > datetime(2022, 9, 23, 7, 10)) &
                 (current_time < datetime(2022, 9, 23, 7, 31))) |
                ((current_time > datetime(2022, 9, 23, 7, 33)) &
                 (current_time < datetime(2022, 9, 23, 7, 49, 30))) |
                # RF10 bottom overlap
                ((current_time > datetime(2022, 9, 23, 10, 0)) &
                 (current_time < datetime(2022, 9, 23, 10, 3))) |
                ((current_time > datetime(2022, 9, 23, 10, 6)) &
                 (current_time < datetime(2022, 9, 23, 10, 18))) |
                # RF10 intersections
                ((current_time > datetime(2022, 9, 23, 11, 25, 30)) &
                 (current_time < datetime(2022, 9, 23, 11, 26, 30))) |
                ((current_time > datetime(2022, 9, 23, 13, 29)) &
                 (current_time < datetime(2022, 9, 23, 13, 42))) |
                ((current_time > datetime(2022, 9, 23, 13, 44)) &
                 (current_time < datetime(2022, 9, 23, 13, 46))) |
                ((current_time > datetime(2022, 9, 23, 13, 52)) &
                 (current_time < datetime(2022, 9, 23, 13, 54))) |
                ((current_time > datetime(2022, 9, 23, 13, 58)) &
                 (current_time < datetime(2022, 9, 23, 14, 0))) |

                # RF11
                ((current_time > datetime(2022, 9, 26, 9, 24)) &
                 (current_time < datetime(2022, 9, 26, 9, 25, 30))) |
                ((current_time > datetime(2022, 9, 26, 9, 44, 30)) &
                 (current_time < datetime(2022, 9, 26, 9, 45))) |
                ((current_time > datetime(2022, 9, 26, 9, 48)) &
                 (current_time < datetime(2022, 9, 26, 9, 49))) |
                ((current_time > datetime(2022, 9, 26, 10, 0)) &
                 (current_time < datetime(2022, 9, 26, 10, 1))) |

                # RF12
                ((current_time > datetime(2022, 9, 29, 7, 44)) &
                 (current_time < datetime(2022, 9, 29, 7, 45))) |
                ((current_time > datetime(2022, 9, 29, 7, 48)) &
                 (current_time < datetime(2022, 9, 29, 7, 50))) |
                ((current_time > datetime(2022, 9, 29, 10, 54)) &
                 (current_time < datetime(2022, 9, 29, 10, 55, 30)))
                ):
                print("skipping flyover")
                continue

            df = pd.DataFrame({
                "POB": ds_point["prs"],
                "QOB": ds_point["Specific_Humidity"],
                "TOB": ds_point["Tv"],
                "ZOB": ds_point["altitude"]})
            df = df[df["ZOB"] > 1000]
            if "QOB" in config.deny_variables:
                df = df.assign(QOB=np.nan)
            if "TOB" in config.deny_variables:
                df = df.assign(TOB=np.nan)
            df.dropna(subset=["QOB", "TOB"], how="all", inplace=True)
            df.fillna(10e10, inplace=True)
    
            if df.size:
                df.to_csv("/tmp/hamsr_processed.csv", index=False,
                    columns=["POB", "QOB", "TOB", "ZOB"], header=False)

                for prepbufr_filename in config.hamsr_prepbufr_filenames:
                    print("adding data to", prepbufr_filename(date))
                    Path(config.prepbufr_dir(date)).mkdir(parents=True, exist_ok=True)
                    subprocess.run(
                        ["/tmp/prepbufr_encode_upperair_hamsr.exe",
                        f"/tmp/prepbufr_{date:%Y%m%d}/{prepbufr_filename(date)}",
                        f"{date:%Y%m%d%H}", f"{ds_point['lon'].values + 360}",
                        f"{ds_point['lat'].values}", f"{dt}",
                        "/tmp/hamsr_processed.csv"])
    subprocess.run(f"rm /tmp/{hamsr_filename}", shell=True)

for date in pd.date_range(config.start_date, config.end_date, freq="1d"):
    subprocess.run(
        f"mv /tmp/prepbufr_{date:%Y%m%d}/* {config.prepbufr_dir(date)}",
        shell=True)
subprocess.run("rm /tmp/hamsr_processed.csv", shell=True)
subprocess.run("rm -rf /tmp/lib", shell=True)
subprocess.run("rm /tmp/prepbufr_encode_upperair_hamsr.exe", shell=True)
