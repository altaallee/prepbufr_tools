import sys
sys.path.insert(1, "../dev/plotters/")
from datetime import datetime
from python_imports import extra
from pathlib import Path


dawn_dir = "../CPEX-CV/data_preliminary/DAWN/"
dawn_filename = ""
dawn_output_dir = "postprocessed_obs/CPEX-CV/DAWN/"
dawn_average_dx = 12000

trim_plot = False
trim_start = datetime(2022, 9, 1)
trim_end = datetime(2022, 10, 1)

if trim_plot:
    ds_dawn = extra.get_dawn_data(
        filename=f"{dawn_dir}/{dawn_filename}", start=trim_start, end=trim_end,
        preliminary=True)
else:
    ds_dawn = extra.get_dawn_data(
        filename=f"{dawn_dir}/{dawn_filename}", preliminary=True)

ds_dawn_avg = extra.full_average_dawn(
    ds_dawn, dawn_average_dx, extra.vertical_levels(),
    ["Wind_Speed", "U_comp", "V_comp"],
    along_track_vars=["AC_Roll", "AC_Pitch", "AC_Altitude"])

Path(dawn_output_dir).mkdir(parents=True, exist_ok=True)
ds_dawn_avg.to_netcdf(
    f"{dawn_output_dir}/{dawn_filename}_full_averaged_{dawn_average_dx}{f'_{trim_start:%Y%m%d%H%M}_{trim_end:%Y%m%d%H%M}' if trim_plot else ''}.nc")