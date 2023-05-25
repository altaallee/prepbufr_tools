from datetime import datetime, timedelta
import pandas as pd
import subprocess
from io import StringIO
from pathlib import Path


start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 30, 18)
freq = timedelta(hours=6)

gdas_dir = lambda date: f"../CPEX-CV/GDAS_R0_HALO_R1/{date:%Y%m%d}/"
prepbufr_filename = lambda date: f"dropsonde.t{date:%H}z.prepbufr.nr"
text_data_file = "decoded_dropsonde_data"
output_dir = "decoded_appended_dropsonde_text"

Path(output_dir).mkdir(parents=True, exist_ok=True)

for date in pd.date_range(start_date, end_date, freq=freq):
    print(date)

    if Path(f"{gdas_dir(date)}/{prepbufr_filename(date)}").is_file():
        subprocess.run(f"rm {text_data_file}", shell=True)
        subprocess.run(
            f"./prepbufr_write_dropsonde.exe {gdas_dir(date)}/{prepbufr_filename(date)} {text_data_file}",
            shell=True)
        with open(text_data_file) as f:
            for block in  f.read().split("message\n"):
                if block != "":
                    header, data = block.split("\n", 1)
                    header = header.split()
                    if float(header[0]) > 320:
                        print(header)
                        df = pd.read_csv(
                            StringIO(data), delim_whitespace=True,
                            names=["pres", "q", "vt", "alt", "u_wind", "v_wind"])
                        df.to_csv(
                                f"{output_dir}/sonde_{date:%Y%m%d%H}_{int(float(header[3]))}_{header[0]}_{header[1]}_{header[2]}",
                            index=False)

subprocess.run(f"rm {text_data_file}", shell=True)
