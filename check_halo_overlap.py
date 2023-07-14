import sys
sys.path.insert(1, "../plotters_cv")
from python_imports import config, mapper, extra
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import subprocess
from io import StringIO
import collections


start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 30, 18)
freq = timedelta(hours=6)

gdas_dir = lambda date: f"../CPEX-CV/GDAS_R0_HALO_R1/{date:%Y%m%d}/"
prepbufr_filename = lambda date: f"halo.t{date:%H}z.prepbufr.nr"
text_data_file = "decoded_halo_data"
images_dir = "overlap_maps/"

Path(images_dir).mkdir(parents=True, exist_ok=True)

for date in pd.date_range(start_date, end_date, freq=freq):
    print(date)

    if Path(f"{gdas_dir(date)}/{prepbufr_filename(date)}").is_file():
        subprocess.run(f"rm {text_data_file}", shell=True)
        subprocess.run(
            f"./prepbufr_write_all.exe {gdas_dir(date)}/{prepbufr_filename(date)} {text_data_file}",
            shell=True)

        lons = []
        lats = []
        num_obs = []
        with open(text_data_file) as f:
            for block in  f.read().split("message\n"):
                if block != "":
                    header, data = block.split("\n", 1)
                    header = header.split()
                    if float(header[0]) > 320:
                        lons.append(float(header[0]))
                        lats.append(float(header[1]))
                        df = pd.read_csv(
                            StringIO(data), delim_whitespace=True,
                            names=["pres", "q", "vt", "alt", "u_wind", "v_wind"])
                        num_obs.append(len(df.index))

        count = collections.Counter(
            [(lon - 360, lat) for lon, lat in zip(lons, lats)])
        count = {key: value for key, value in count.items() if value > 1}
        if count != {}:
            print(count)

        map_img = mapper.SingleMap()
        ax = map_img.get_ax()
        extra.draw_metnav_flightpath(
            ax,
            f"../plotters_cv/flight_paths/{config.metnav_flightpath_filename_dynamic[date.floor(freq='D')]}",
            start=date - freq / 2, end=date + freq / 2, color="red")

        map_img.draw_scatter(
            lons, lats, c=num_obs, linestyle="None", marker="x", norm=False,
            zorder=9)
        
        map_img.draw_title(f"HALO {date:%Y-%m-%d %HZ}")
        map_img.draw_shapefiles()
        map_img.draw_gridlines()
        map_img.save_image(images_dir, f"halo_{date:%Y%m%d%H}")

subprocess.run(f"rm {text_data_file}", shell=True)
