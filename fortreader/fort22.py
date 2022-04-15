import logging
import numpy as np

# Read FORT.22 file (v53 | NWS=8)
# -------------------------------
# yes
def read_fort22(filename):
    """
    Read in fort.22 file and create a file to plot out the path!
    """
    
    logging.info('Reading in data from fort.22...')

    
    lon_lat_array = []
    
    for line in open(filename):
        line_array = line.split()
        lat = line_array[6]
        lon = line_array[7]
        
        # check lon letter
        if lon[-2] == 'E':
            lon = float(lon[0:len(lon)-2]) / 10
        else:
            lon = -float(lon[0:len(lon)-2]) / 10
        
        # check lat letter
        if lat[-2] == 'N':
            lat = float(lat[0:len(lat)-2]) / 10
        else:
            lat = -float(lat[0:len(lat)-2]) / 10
            
        # add to array
        lon_lat_array.append([lon, lat])
        
    return lon_lat_array
