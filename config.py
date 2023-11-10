from datetime import datetime, timedelta


start_date = datetime(2022, 9, 4, 0)
end_date = datetime(2022, 9, 30, 18)
frequency = timedelta(hours=6)

skip = 1
num_levels = "model"
num_levels_dropsonde = 45

deny_variables = [
    #"QOB",
    #"TOB",
    #"UOB",
    #"VOB",
]

prepbufr_dir = lambda date: f"../CPEX-CV/test5/{date:%Y%m%d}/"

dawn_data_dir = "postprocessed_obs/CPEX-CV/DAWN/with_pressure/45_model_levels/"
dawn_prepbufr_filenames = [
    lambda date: f"gdas_dawn_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_dawn_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_halo_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_dawn_halo_hamsr.t{date:%H}z.prepbufr.nr",

    #lambda date: f"gdas_qv_t.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_qv_uv.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_t_uv.t{date:%H}z.prepbufr.nr",

    lambda date: f"dawn.t{date:%H}z.prepbufr.nr",
]
dawn_filenames = [
    "cpexcv-DAWN_DC8_20220906_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220907_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220909_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220910_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220914_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220915_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220916_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220920_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220922_R0.nc_full_averaged_12000.nc",
    #"cpexcv-DAWN_DC8_20220922_R0.nc_full_averaged_12000.nc_overlap_202209221003_202209221205.nc",
    "cpexcv-DAWN_DC8_20220923_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220926_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220929_R0.nc_full_averaged_12000.nc",
    "cpexcv-DAWN_DC8_20220930_R0.nc_full_averaged_12000.nc",
]

dropsonde_data_dir = "../CPEX-CV/data_R0/dropsonde/"
dropsonde_prefix = "CPEX_AVAPS_RD41_v1_2022*"
decoded_gdas_dropsonde_dir = "decoded_gdas_dropsonde_text"
dropsonde_prepbufr_filenames = [
    lambda date: f"gdas_dawn_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_dawn_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_halo_sonde.t{date:%H}z.prepbufr.nr",

    #lambda date: f"gdas_qv_t.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_qv_uv.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_t_uv.t{date:%H}z.prepbufr.nr",

    lambda date: f"dropsonde.t{date:%H}z.prepbufr.nr",
]

halo_data_dir = "postprocessed_obs/CPEX-CV/HALO/with_pressure/45_model_levels_2pqc/"
halo_prepbufr_filenames = [
    lambda date: f"gdas_dawn_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_halo_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_dawn_halo_hamsr.t{date:%H}z.prepbufr.nr",

    #lambda date: f"gdas_qv_t.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_qv_uv.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_t_uv.t{date:%H}z.prepbufr.nr",

    lambda date: f"halo.t{date:%H}z.prepbufr.nr",
]
halo_filenames = [
#    "CPEXCV-HALO_DC8_20220903_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220906_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220907_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220909_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220910_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220914_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220915_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220916_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220920_R1.h5_full_averaged_12000.nc",
    "CPEXCV-HALO_DC8_20220922_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220922_R1.h5_full_averaged_12000.nc_overlap_202209221003_202209221200.nc",
    #"CPEXCV-HALO_DC8_20220923_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220926_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220929_R1.h5_full_averaged_12000.nc",
    #"CPEXCV-HALO_DC8_20220930_R1.h5_full_averaged_12000.nc",
]

hamsr_data_dir = "postprocessed_obs/CPEX-CV/HAMSR/45_model_levels/"
hamsr_filenames = [
    "CPEXCV-HAMSR-data_DC8_20220906_nadir.nc_full_averaged_12000_combined.nc", 
    "CPEXCV-HAMSR-data_DC8_20220907_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220909_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220910_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220914_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220915_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220916_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220920_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220922_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220922_nadir.nc_full_averaged_12000_combined.nc_overlap_202209221003_202209221205.nc",
    "CPEXCV-HAMSR-data_DC8_20220923_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220926_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220929_nadir.nc_full_averaged_12000_combined.nc",
    "CPEXCV-HAMSR-data_DC8_20220930_nadir.nc_full_averaged_12000_combined.nc",
]
hamsr_prepbufr_filenames = [
    lambda date: f"gdas_dawn_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_dawn_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_dawn_halo_hamsr.t{date:%H}z.prepbufr.nr",

    #lambda date: f"gdas_qv_t.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_qv_uv.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_t_uv.t{date:%H}z.prepbufr.nr",

    lambda date: f"hamsr.t{date:%H}z.prepbufr.nr",
]

radiosonde_data_dir = "../CPEX-CV/data_R0/radiosonde/"
radiosonde_prefix = "cpexcv-radiosonde-netcdf_SONDE*"
radiosonde_prepbufr_filenames = [
    lambda date: f"gdas_dawn_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_halo_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_dawn_hamsr_sonde.t{date:%H}z.prepbufr.nr",
    lambda date: f"gdas_dawn_halo_sonde.t{date:%H}z.prepbufr.nr",

    #lambda date: f"gdas_qv_t.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_qv_uv.t{date:%H}z.prepbufr.nr",
    #lambda date: f"gdas_t_uv.t{date:%H}z.prepbufr.nr",

    lambda date: f"radiosonde.t{date:%H}z.prepbufr.nr",
]
