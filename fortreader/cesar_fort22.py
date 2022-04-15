import logging
import numpy as np
import math

def read_fort22_cesar(filename, time_slice):
    """
    Read in cesar's custom fort.22 file and create a file sutable for gmt plot!
    """
    
    logging.info('Reading in data from fort.22...')
    
    with open(filename) as fort22:
    
        logging.debug('Skipping %i time slices totalling %i data points...' % (time_slice, time_slice*140000))
        
        # Skip time_slices not needed
        for _ in range(time_slice*(280*500)):
            fort22.readline()
        
        wind_vel_data = np.zeros((280, 500, 4))
        
        # Assume data starts from top left
        lon_start = -101.0
        lat_start = 32.0
        
        logging.debug('Reading in 140000 nodes...')
        # Assume data reads from left to right
        for grid_lat in range(280):
            for grid_lon in range(500):
                (x_vel, y_vel, pressure) = [float(s) for s in fort22.readline().split()]
                
                theta = math.degrees(math.atan2(y_vel, x_vel))
                
                # Caltulate length
                length = math.sqrt((x_vel**2)+(y_vel**2))
                
                wind_vel_data[grid_lat][grid_lon] = [lon_start+(grid_lon*0.05), lat_start-(grid_lat*0.05), theta, length]

        return wind_vel_data
