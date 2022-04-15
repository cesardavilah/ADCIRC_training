 #!/bin/sh
 
# Generate CSV from current data
# Arg 1 - Dir to search for fort files
# Arg 2 - Timeslice to process out of data (NOTE: Some of the later times do not work with the new ADCIRC format!)
# Arg 3 - Leave as '-1', artifact of old script for processing to figures
python ./main.py . 100 -1

# Create tiff file of the LAG MOD
gdal_grid -zfield field_3 -txe -97.6688234727488549 -95.9583619884986803 -tye 26.0010747185894786 27.1244897802529046 -a invdistnn:smoothing=0.1:radius=0.002:max_points=3:nodata=-99 -tr 0.001 0.001 -of GTiff -ot Float64 -l fort63 dem.vrt dem.tiff
