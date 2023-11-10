import argparse

parser = argparse.ArgumentParser(description="Average DAWN data.")
parser.add_argument(
    "--filename", required=True, type=str, help="Name of DAWN file.")
parser.add_argument(
    "--directory", default="../CPEX-CV/data_R0/DAWN/", type=str,
    help="Directory of DAWN file.")
parser.add_argument(
    "--output_dir", default="postprocessed_obs/CPEX-CV/DAWN/", type=str,
    help="Directory to output file.")
parser.add_argument(
    "--dx", default=12000, type=int,
    help="Horizontal average distance in meters.")
parser.add_argument(
    "--vertical_levels", default="model", help="Number of vertical levels.")
parser.add_argument(
    "--trim_plot", default=False, type=bool,
    help="Trim data to date range.")
parser.add_argument(
    "--trim_start", default="202209010000", type=str,
    help="Start time to trim data. (YYYYMMDDhhmm)")
parser.add_argument(
    "--trim_end", default="202210010000", type=str,
    help="End time to trim data. (YYYYMMDDhhmm)")

args = parser.parse_args()

import sys
sys.path.insert(1, "../plotters_cv/")
import subprocess
from datetime import datetime
from python_imports import extra
from pathlib import Path


subprocess.run(f"cp {args.directory}/{args.filename} /tmp", shell=True)

if args.trim_plot:
    trim_start = datetime.strptime(args.trim_start, "%Y%m%d%H%M")
    trim_end = datetime.strptime(args.trim_end, "%Y%m%d%H%M")
    ds_dawn = extra.get_dawn_data(
        filename=f"/tmp/{args.filename}", start=trim_start, end=trim_end)
else:
    ds_dawn = extra.get_dawn_data(filename=f"/tmp/{args.filename}")

ds_dawn_avg = extra.full_average_dawn(
    ds_dawn, args.dx, extra.vertical_levels(args.vertical_levels),
    ["Wind_Speed", "U_comp", "V_comp"],
    along_track_vars=["AC_Roll", "AC_Pitch", "AC_Altitude"])

Path(args.output_dir).mkdir(parents=True, exist_ok=True)
ds_dawn_avg.to_netcdf(
    f"{args.output_dir}/{args.filename}_full_averaged_{args.dx}{f'_{trim_start:%Y%m%d%H%M}_{trim_end:%Y%m%d%H%M}' if args.trim_plot else ''}.nc")
