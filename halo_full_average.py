import sys
sys.path.insert(1, "../dev/plotters/")
from datetime import datetime
from python_imports import extra
from pathlib import Path


halo_dir = "../CPEX-CV/data_preliminary/HALO/"
halo_filename = ""
halo_output_dir = "postprocessed_obs/CPEX-CV/HALO/"
halo_average_dx = 12000

trim_plot = False
trim_start = datetime(2022, 9, 1)
trim_end = datetime(2022, 10, 1)

if trim_plot:
    ds_halo = extra.get_halo_data(
        filename=f"{halo_dir}/{halo_filename}", start=trim_start, end=trim_end,
        preliminary=True)
else:
    ds_halo = extra.get_halo_data(
        filename=f"{halo_dir}/{halo_filename}", preliminary=True)

ds_halo_avg = extra.full_average_halo(
    ds_halo, halo_average_dx, extra.vertical_levels(), ["h2o_mmr_v"])

Path(halo_output_dir).mkdir(parents=True, exist_ok=True)
ds_halo_avg.to_netcdf(
    f"{halo_output_dir}/{halo_filename}_full_averaged_{halo_average_dx}{f'_{trim_start:%Y%m%d%H%M}_{trim_end:%Y%m%d%H%M}' if trim_plot else ''}.nc")