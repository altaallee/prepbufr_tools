import sys
sys.path.insert(1, "../plotters_cv/")
from python_imports import extra
from datetime import datetime
import glob
import pandas as pd
from pathlib import Path
import metpy.calc as mpcalc
from metpy.units import units
import matplotlib.pyplot as plt
plt.switch_backend("Agg")


start_date = datetime(2022, 9, 22, 0)
end_date = datetime(2022, 9, 24, 0)

dropsonde_dir = "../CPEX-CV/data_R0/dropsonde/"
dropsonde_prefix = "CPEX_AVAPS_RD41_v1_202209*"
decoded_appended_dropsonde_dir = "decoded_appended_dropsonde_text"
decoded_gdas_dropsonde_dir = "decoded_gdas_dropsonde_text"
output_dir = "dropsonde_original_gdas_averaged_images"

filenames = glob.glob(f"{dropsonde_dir}/{dropsonde_prefix}*")

Path(output_dir).mkdir(parents=True, exist_ok=True)

for filename in sorted(filenames):
    print(filename)

    df, launch_time = extra.get_dropsonde_data(filename, subset="pres")

    if (launch_time > start_date) and (launch_time < end_date) and (len(df["pres"])):
        lon = round(df["reference_lon"][0] + 360, 1)
        lat = round(df["reference_lat"][0], 1)
        date = df["reference_time"][0]

        df_mass, _ = extra.get_dropsonde_data(
            filename, subset=["pres", "vt", "mr"])
        df_wind, _ = extra.get_dropsonde_data(
            filename, subset=["pres", "u_wind", "v_wind"])
        df_mass["q"] = mpcalc.specific_humidity_from_mixing_ratio(
            df_mass["mr"]).to(units("milligrams / kilogram")).m

        fig, axes = plt.subplots(
            nrows=1, ncols=4, figsize=[10, 8], sharey=True)

        if len(df_mass["pres"]):
            axes[0].plot(
                df_mass["vt"].m - 273.15, df_mass["pres"], linestyle="None",
                color="silver", marker=".", label="Original")
            axes[1].plot(
                df_mass["q"] / 1000, df_mass["pres"], linestyle="None",
                color="silver", marker=".", label="Original")
        if len(df_wind["pres"]):
            axes[2].plot(
                df_wind["u_wind"], df_wind["pres"], linestyle="None",
                color="silver", marker=".", label="Original")
            axes[3].plot(
                df_wind["v_wind"], df_wind["pres"], linestyle="None",
                color="silver", marker=".", label="Original")

        mass_file = glob.glob(
            f"{decoded_appended_dropsonde_dir}/sonde_{date:%Y%m%d}??_132_{lon}_{lat}_*")
        if len(mass_file):
            df_mass = pd.read_csv(mass_file[0], na_values=[100000000000])
            axes[0].plot(
                df_mass["vt"], df_mass["pres"], linestyle="None",
                color="tab:green", marker=".", label="Appended")
            axes[1].plot(
                df_mass["q"] / 1000, df_mass["pres"], linestyle="None",
                color="tab:green", marker=".", label="Appended")

        wind_file = glob.glob(
            f"{decoded_appended_dropsonde_dir}/sonde_{date:%Y%m%d}??_232_{lon}_{lat}_*")
        if len(wind_file):
            df_wind = pd.read_csv(wind_file[0], na_values=[100000000000])
            axes[2].plot(
                df_wind["u_wind"], df_wind["pres"], linestyle="None",
                color="tab:green", marker=".", label="Appended")
            axes[3].plot(
                df_wind["v_wind"], df_wind["pres"], linestyle="None",
                color="tab:green", marker=".", label="Appended")

        mass_file = glob.glob(
            f"{decoded_gdas_dropsonde_dir}/sonde_{date:%Y%m%d}??_132_{lon}_{lat}_*")
        if len(mass_file):
            df_mass = pd.read_csv(mass_file[0], na_values=[100000000000])
            axes[0].plot(
                df_mass["vt"], df_mass["pres"], linestyle="None",
                color="tab:red", marker=".", label="GDAS")
            axes[1].plot(
                df_mass["q"] / 1000, df_mass["pres"], linestyle="None",
                color="tab:red", marker=".", label="GDAS")

        wind_file = glob.glob(
            f"{decoded_gdas_dropsonde_dir}/sonde_{date:%Y%m%d}??_232_{lon}_{lat}_*")
        if len(wind_file):
            df_wind = pd.read_csv(wind_file[0], na_values=[100000000000])
            axes[2].plot(
                df_wind["u_wind"], df_wind["pres"], linestyle="None",
                color="tab:red", marker=".", label="GDAS")
            axes[3].plot(
                df_wind["v_wind"], df_wind["pres"], linestyle="None",
                color="tab:red", marker=".", label="GDAS")

        axes[0].set_ylim(1020, 200)
        axes[0].legend()
        axes[0].set_xlabel("T")
        axes[1].set_xlabel("q")
        axes[2].set_xlabel("U")
        axes[3].set_xlabel("V")
        axes[0].set_ylabel("Pressure")
        plt.suptitle(filename.split("/")[-1])

        fig.savefig(f"{output_dir}/sonde_{date:%Y%m%d}_{lon}_{lat}.png")
        plt.close()
