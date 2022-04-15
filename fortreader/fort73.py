"""Handles fort.73 files"""

import logging
import numpy as np

def read_fort73(filename, time_slice):
    """
    Reads in Fort.73 and outputs data for given time_slice.
    Follows the v53 specificatons.
    """

    logging.info('Reading in data from fort.73...')

    with open(filename) as fort73:

        logging.debug('Reading in fort.73 header data...')

        (_, _, _) = fort73.readline().split()
        (num_datasets, num_nodes, _, _, _, _, _) = fort73.readline().split()

        num_datasets = int(num_datasets)
        num_nodes = int(num_nodes)

        vector_data = np.zeros((num_nodes, 1))

        if time_slice >= num_datasets:
            logging.error('Time slice %i is out of bounds! %i is the limit!',
                          time_slice,
                          num_datasets-1)
            raise IndexError

        logging.debug('Reading in %i sets of %i nodes', num_datasets, num_nodes)

        # Skip unused time frames
        for _ in range(time_slice):
            fort73.readline()
            for _ in range(num_nodes):
                fort73.readline()


        (_, _) = fort73.readline().split()

        for node in range(num_nodes):
            (_, press) = [float(s) for s in fort73.readline().split()]
            vector_data[node] = press

        logging.debug('Done reading!')
        logging.debug("Here's a peek into the data: %s", vector_data)

        return vector_data
