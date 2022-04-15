import logging
import numpy as np

# Read FORT.64 file (v53)
# -----------------------
# RUNDES, RUNID, AGRID
# NDSETSV, NP, DTDP*NSPOOLGV, NSPOOLGV, IRTYPE
# TIME, IT
#
# k=1 to NP
#   k, UU2(k), VV2(k)
#

def read_fort64(filename):
    logging.info('Reading in data from fort.64 file...')

    with open(filename) as fort64:
        (_, _, _) = fort64.readline().split()

        (num_datasets, num_nodes, _, _, _, _, _) = fort64.readline().split()

        num_datasets = int(num_datasets)
        num_nodes = int(num_nodes)

        vector_data = np.zeros((num_datasets, num_nodes, 2))

        logging.debug(
            'Reading in %i sets of %i nodes' %
            (num_datasets, num_nodes))

        for dataset in range(num_datasets):
            (_, _) = fort64.readline().split()

            for node in range(num_nodes):
                (_, x, y) = [float(s) for s in fort64.readline().split()]
                vector_data[dataset][node] = [x, y]

        logging.debug('Done reading!')
        logging.debug("Here's a peek into the data: {}".format(vector_data))

        return vector_data
