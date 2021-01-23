# Converting a Jupyter Notebook to a script #

Jupyter notebooks are great for developing a method but what about if you need to run the method for lots of files? This tutorial describe how to go from a notebook to a script which you can run on the command line and apply to multiple files.

For this example we'll be using a notebook written to calculate the Floating Debris Index (FDI; [1]) and apply to a Sentinel 2 netCDF file processed using ACOLITE. If you are interested in running the notebook a tutorial on using ACOLITE is available from a [NEODAAS training course](https://data.neodaas.ac.uk/files/training_october_2020/). You can download ACOLITE and the manual from [here](https://odnature.naturalsciences.be/remsem/software-and-data/acolite). The [xarray](http://xarray.pydata.org/en/stable/) library is used to read the netCDF file, calculate FDI and write back out to a netCDF file.

[1] Biermann, L., Clewley, D., Martinez-Vicente, V. et al. Finding Plastic Patches in Coastal Waters using Optical Satellite Data. Sci Rep 10, 5364 (2020). https://doi.org/10.1038/s41598-020-62298-z

## 1. Tidy up notebook ##

The first step is to tidy up the notebook so it only contains the code that is required. This means removing cells which print out lots of data or produce plots (unless plots are an output of the notebook).

## 2. Export as Python ##

From File -> Export Notebook As... in the Jupyter Lab menu select 'Export Notebook to Excecutable Script'. This will give you a Python script to download.

If you copy the script to the same directory as the notebook and either open a terminal / command prompt and navigate to this directory or select 'File' -> 'New' -> Terminal in Jupter Lab to open a terminal within your browser you can run the script using `python SCRIPT_NAME` so for this example:
```
python s2_FDI_Calculation.py
```

This allows running the script outside a notebook. However, it will only run the netCDF file which has been 'hard coded' in the script, we want to be able to specify the input file on the command line.

## 3. Allow specifying input file using argparse ##

The input and output file are specified in the lines:
```
s2_data = xarray.open_dataset("S2A_MSI_2018_04_20_11_21_21_T30VWH_L2R.nc", decode_cf=False, chunks=512)
```
and:
```
fdi_xarray.to_netcdf("S2A_MSI_2018_04_20_11_21_21_T30VWH_L2R_fdi.nc", engine="netcdf4", encoding={"fdi" : {"zlib" : True, "complevel" : 4}})
```
Using [argparse](https://docs.python.org/3/library/argparse.html) it is possible to specify file names (any many other parameters) from the command line.

For example:

```python
import argparse
parser = argparse.ArgumentParser(description="Calculate Floating Debris Index (FDI) Biermann "
                                                " to a S2 scene")
parser.add_argument("innetcdf", help="Input netCDF file")
parser.add_argument("outnetcdf", help="Output netCDF file")
args = parser.parse_args()
```
Adding this at the start of the script and changing the lines
```
s2_data = xarray.open_dataset(args.innetcdf, decode_cf=False, chunks=512)
```
and:
```
fdi_xarray.to_netcdf(args.outnetcdf engine="netcdf4", encoding={"fdi" : {"zlib" : True, "complevel" : 4}})
```
Trying to run the script as before using `python s2_FDI_Calculation.py` will now print the following message:

```
usage: s2_FDI_Calculation.py [-h] innetcdf outnetcdf
s2_FDI_Calculation.py: error: the following arguments are required: innetcdf, outnetcdf
```
So argparse not only allows taking arguments from the command line it also provides help if the correct arguments aren't provided.
The script can now be run using:
```
python s2_FDI_Calculation.py S2A_MSI_2018_04_20_11_21_21_T30VWH_L2R.nc S2A_MSI_2018_04_20_11_21_21_T30VWH_L2R_fdi.nc
```
Providing a different input and output file will allow running for different files. However, an improvement would be allow the script to take multiple input files and run for all of them rather than having to run the script for each file.

## 4. Tidy up script to use functions ##

To make it easier to run multiple files the code which calculates FDI will be split into a separate function:

```python

def calculate_fdi_from_netcdf(input_netcdf, output_netcdf):
    """
    Function to calculate FDI from a netCDF file
    """
    # Specify chunksize so uses dask and doesn't load all data to RAM
    s2_data = xarray.open_dataset(input_netcdf, decode_cf=False, chunks=512)
    .
    .
    .
    # Export
    print("Writing out")
    with ProgressBar():
        fdi_xarray.to_netcdf(output_netcdf, engine="netcdf4", encoding={"fdi" : {"zlib" : True, "complevel" : 4}})
```

The argparse lines are them moved to the bottom of the script:
```python
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Calculate Floating Debris Index (FDI) Biermann "
                                                    " to a S2 scene")
    parser.add_argument("innetcdf", help="Input netCDF file")
    parser.add_argument("outnetcdf", help="Output netCDF file")
    args = parser.parse_args()

    calculate_fdi_from_netcdf(args.innetcdf, args.outnetcdf)
```
This will only run if the the file is run as a script, allowing the function to be used in another Python script. For more details see [here](https://docs.python.org/3/library/__main__.html).

As part of the tidying up process comments with cell numbers from the notebook (e.g., `# In[3]:`) can be removed.

This will run the same as before, so a single input and output file is provided. The next step is to take a number of input files, an output directory and run for all of them:

```python
import os

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

```
This time rather than specifying an output netCDF an output directory is used (specified with `-o` or `--outdir` when running the script) and the os module is used to build a path using the input file.

The script can now be run using:
```
python s2_FDI_Calculation.py S2A_MSI_2018_04_20_11_21_21_T30VWH_L2R.nc S2A_MSI_2018_06_07_08_56_01_T35SMD_L2R.nc -o .
```
To calculate from two netCDF files and save to the current directory (specified with `.`). On macOS and Linux can use globs to match a list of files rather than specifying, for example:

```
python s2_FDI_Calculation.py S2A_MSI_*_L2R.nc -o .
```



