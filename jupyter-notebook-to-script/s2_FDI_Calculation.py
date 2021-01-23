#!/usr/bin/env python
# coding: utf-8

# # Calculate Floating Debris Index
# 
# A notebook to calculate the Floating Debris Index (FDI; [1]) and apply to a Sentinel 2 netCDF file processed using ACOLITE
# 
# [1] Biermann, L., Clewley, D., Martinez-Vicente, V. et al. Finding Plastic Patches in Coastal Waters using Optical Satellite Data. Sci Rep 10, 5364 (2020). https://doi.org/10.1038/s41598-020-62298-z

import argparse
import os
import xarray # Used to read and manipulate netCDF
from dask.diagnostics import ProgressBar # Dask is used to process large netCDF without loading all to RAM this shows progress

def calculate_fdi_from_netcdf(input_netcdf, output_netcdf):

    # Specify chunksize so uses dask and doesn't load all data to RAM
    s2_data = xarray.open_dataset(input_netcdf, decode_cf=False, chunks=512)
    
    nir =  s2_data["rhos_833"]
    # Try S2A and S2B wavelengths
    try:
        red_edge =  s2_data["rhos_740"]
    except KeyError:
        red_edge =  s2_data["rhos_739"]
    try:
        swir = s2_data["rhos_1614"]
    except KeyError:
        swir = s2_data["rhos_1610"]
    
    # Calculate FDI
    fdi = nir - red_edge - (swir - red_edge)*1.636
    # Set dataset name to FDI
    fdi.name = "FDI"
    
    # Convert to dataset
    fdi_xarray = fdi.to_dataset(name="fdi")
    
    # Write out to netCDF
    # Set up attributes
    fdi_xarray["fdi"].attrs = {'long_name': 'Floating Debris Index',
                            'standard_name': 'mass_concentration_of_chlorophyll_a_in_sea_water'}
    
    # Export
    print("Writing out")
    with ProgressBar():
        fdi_xarray.to_netcdf(output_netcdf, engine="netcdf4", encoding={"fdi" : {"zlib" : True, "complevel" : 4}})


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Calculate Floating Debris Index (FDI) Biermann "
                                                    " to a S2 scene")
    parser.add_argument("innetcdfs", nargs="+", help="Input netCDF file (s)")
    parser.add_argument("-o", "--outdir", help="Output directory", required=True)
    args = parser.parse_args()

    for in_netcdf in args.innetcdfs:
        print(f"Calculating FDI for {in_netcdf}...")
        # Set up output name for FDI netCDF
        out_netcdf_basename = os.path.basename(in_netcdf).replace(".nc", "_fdi.nc")
        out_netcdf = os.path.join(args.outdir, out_netcdf_basename)
        # Calculate FDI
        calculate_fdi_from_netcdf(in_netcdf, out_netcdf)
        print(f"Saved to {out_netcdf}")

