from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import subprocess

start_date = datetime(2022, 9, 22, 0)
end_date = datetime(2022, 9, 22, 18)
freq = timedelta(hours=6)

gdas_dir = lambda date: f"../CPEX-CV/GDAS_org/{date:%Y%m%d}/"
prepbufr_filename = lambda date: f"gdas.t{date:%H}z.prepbufr.nr"
destination_dir = lambda date: f"../CPEX-CV/test5/{date:%Y%m%d}/"
dawn_filename = lambda date: f"gdas_dawn.t{date:%H}z.prepbufr.nr"
dropsonde_filename = lambda date: f"gdas_dropsonde.t{date:%H}z.prepbufr.nr"
halo_filename = lambda date: f"gdas_halo.t{date:%H}z.prepbufr.nr"
radiosonde_filename = lambda date: f"gdas_radiosonde.t{date:%H}z.prepbufr.nr"
dawn_dropsonde_halo_filename = lambda date: f"gdas_dawn_dropsonde_halo.t{date:%H}z.prepbufr.nr"
dawn_dropsonde_halo_radiosonde_filename = lambda date: f"gdas_dawn_dropsonde_halo_radiosonde.t{date:%H}z.prepbufr.nr"

dawn_halo_hamsr_sonde_filename = lambda date: f"gdas_dawn_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr"
halo_hamsr_sonde_filename = lambda date: f"gdas_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr"
dawn_hamsr_sonde_filename = lambda date: f"gdas_dawn_hamsr_sonde.t{date:%H}z.prepbufr.nr"
dawn_halo_sonde_filename = lambda date: f"gdas_dawn_halo_sonde.t{date:%H}z.prepbufr.nr"
dawn_halo_hamsr_filename = lambda date: f"gdas_dawn_halo_hamsr.t{date:%H}z.prepbufr.nr"

qv_t_filename = lambda date: f"gdas_qv_t.t{date:%H}z.prepbufr.nr"
qv_uv_filename = lambda date: f"gdas_qv_uv.t{date:%H}z.prepbufr.nr"
t_uv_filename = lambda date: f"gdas_t_uv.t{date:%H}z.prepbufr.nr"

for date in pd.date_range(start_date, end_date, freq=freq):
    print(date)
    Path(f"{destination_dir(date)}").mkdir(parents=True, exist_ok=True)
    # GDAS only
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{prepbufr_filename(date)}",
        shell=True)

    # GDAS + DAWN + HALO + HAMSR + SONDE
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_halo_hamsr_sonde_filename(date)}",
        shell=True)
    # GDAS + HALO + HAMSR + SONDE
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{halo_hamsr_sonde_filename(date)}",
        shell=True)
    # GDAS + DAWN + HAMSR + SONDE
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_hamsr_sonde_filename(date)}",
        shell=True)
    # GDAS + DAWN + HALO + SONDE
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_halo_sonde_filename(date)}",
        shell=True)
    # GDAS + DAWN + HALO + HAMSR
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_halo_hamsr_filename(date)}",
        shell=True)

    # GDAS + qv + t
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{qv_t_filename(date)}",
        shell=True)
    # GDAS + qv + uv
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{qv_uv_filename(date)}",
        shell=True)
    # GDAS + t + uv
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{t_uv_filename(date)}",
        shell=True)

    # GDAS + DAWN
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_filename(date)}",
        shell=True)
    # GDAS + dropsonde
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dropsonde_filename(date)}",
        shell=True)
    # GDAS + HALO
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{halo_filename(date)}",
        shell=True)
    # GDAS + radiosonde
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{radiosonde_filename(date)}",
        shell=True)
    # GDAS + DAWN + dropsonde + HALO
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_dropsonde_halo_filename(date)}",
        shell=True)
    # GDAS + DAWN + dropsonde + HALO + radiosonde
    subprocess.run(
        f"cp {gdas_dir(date)}/{prepbufr_filename(date)} {destination_dir(date)}/{dawn_dropsonde_halo_radiosonde_filename(date)}",
        shell=True)
