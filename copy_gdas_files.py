from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import subprocess

start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 28, 18)
freq = timedelta(hours=6)

gdas_dir = lambda date: f"/nobackupp19/schen4/p7/schen4_nbp1/CPEX_AW/CPEX_CV/data/GDAS_CPEX/{date:%Y%m%d}/"
prepbufr_filename = lambda date: f"gdas.t{date:%H}z.prepbufr.nr"
destination_dir = lambda date: f"../CPEX-CV/GDAS/{date:%Y%m%d}/"
dawn_filename = lambda date: f"gdas_dawn.t{date:%H}z.prepbufr.nr"
dropsonde_filename = lambda date: f"gdas_dropsonde.t{date:%H}z.prepbufr.nr"
halo_filename = lambda date: f"gdas_halo.t{date:%H}z.prepbufr.nr"
dawn_dropsonde_halo_filename = lambda date: f"gdas_dawn_dropsonde_halo.t{date:%H}z.prepbufr.nr"
dawn_halo_filename = lambda date: f"gdas_dawn_halo.t{date:%H}z.prepbufr.nr"

for date in pd.date_range(start_date, end_date, freq=freq):
    print(date)
    Path(f"{destination_dir(date)}").mkdir(parents=True, exist_ok=True)
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{prepbufr_filename(date)}",
        shell=True)
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_filename(date)}",
        shell=True)
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dropsonde_filename(date)}",
        shell=True)
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{halo_filename(date)}",
        shell=True)
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_dropsonde_halo_filename(date)}",
        shell=True)
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_halo_filename(date)}",
        shell=True)