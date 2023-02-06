from pathlib import Path
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from datetime import datetime, timedelta


start_date = datetime(2022, 9, 1, 0)
end_date = datetime(2022, 10, 1, 0)
frequency = timedelta(hours=6)

prepbufr_dir = lambda date: f"../CPEX-CV/GDAS_updated_dawn_halo/{date:%Y%m%d}/"
prepbufr_filename = lambda date: f"dropsonde.t{date:%H}z.prepbufr.nr"
save_filename = lambda date: f"locations_dropsonde_{date:%Y%m%d%H}"

extent = False
wlon = 0 + 360
elon = 0 + 360
slat = 0
nlat = 0

Path('location_files/').mkdir(parents=True, exist_ok=True)
Path('location_plots/').mkdir(parents=True, exist_ok=True)

for date in pd.date_range(start_date, end_date, freq=frequency):
    print(date)

    subprocess.run(
        f"./prepbufr_decode_locations.exe {prepbufr_dir(date)}/{prepbufr_filename(date)} > location_files/locations.{date:%Y%m%d%H}.txt",
        shell=True)

    df = pd.read_csv(
        f"location_files/locations.{date:%Y%m%d%H}.txt", delim_whitespace=True,
        names=["lon", "lat", "hour", "type", "elevation", "sat_id", "report_type"],
        na_values=[100000000000])
    if extent:
        df.where((df["lon"] > wlon) & (df["lon"] < elon) & (df["lat"] > slat) &
            (df["lat"] < nlat), inplace=True)

    fig = plt.figure(figsize=[10, 10])
    ax = fig.add_subplot(111, projection=ccrs.Mercator())
    if extent:
        ax.set_extent([wlon, elon, slat, nlat], crs=ccrs.PlateCarree())

    cm = ax.scatter(
        df["lon"], df["lat"], c=df["type"], transform=ccrs.PlateCarree())
    cb = plt.colorbar(cm, ax=ax)
    cb.set_label("Report Type")

    ax.add_feature(cfeat.COASTLINE)
    ax.add_feature(cfeat.BORDERS)

    ax.set_title(f"GDAS {date:%Y-%m-%d %HZ}")
    gl = ax.gridlines(draw_labels=["bottom", "left"])
    gl.top_labels = False
    gl.right_labels = False

    plt.savefig(f"location_plots/{save_filename(date)}.png")
