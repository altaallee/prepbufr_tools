from pathlib import Path
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
plt.switch_backend("Agg")
import cartopy.crs as ccrs
import cartopy.feature as cfeat
from datetime import datetime, timedelta


start_date = datetime(2022, 9, 1, 0)
end_date = datetime(2022, 10, 1, 0)
frequency = timedelta(hours=6)

prepbufr_dir = lambda date: f"../CPEX-CV/GDAS_org/{date:%Y%m%d}/"
prepbufr_filename = lambda date: f"gdas.t{date:%H}z.prepbufr.nr"
save_filename = lambda date: f"gdas_{date:%Y%m%d%H}"

extent = True
wlon = -61.6 + 360
elon = 17.6 + 360
slat = -6.4
nlat = 39.5

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

    for type_num in df["type"].unique():
        df_type = df[df["type"] == type_num]

        fig = plt.figure(figsize=[10, 10])
        ax = fig.add_subplot(111, projection=ccrs.Mercator())
        if extent:
            ax.set_extent([wlon, elon, slat, nlat], crs=ccrs.PlateCarree())

        ax.scatter(
            df_type["lon"], df_type["lat"], transform=ccrs.PlateCarree())

        ax.add_feature(cfeat.COASTLINE)
        ax.add_feature(cfeat.BORDERS)

        ax.set_title(f"GDAS {int(type_num)} {date:%Y-%m-%d %HZ}")
        gl = ax.gridlines(draw_labels=["bottom", "left"])
        gl.top_labels = False
        gl.right_labels = False

        plt.savefig(f"location_plots/{save_filename(date)}_{int(type_num)}.png")
        plt.close(fig)
