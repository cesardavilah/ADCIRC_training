import logging
import numpy as np

# Read FORT.63 file (v53)
# -----------------------
# RUNDES, RUNID, AGRID                          | RUNDES, RUNID = Run Descriptions 1 & 2    | ARGID = Grid identifier(IDENT)
# NDSETSE, NP, DTDP*NSPOOLGE, NSPOOLGE, IRTYPE  | NDSETSE       = Num datasets to be writen for fort.63
#                                               | NP            = Num nodes in horiz grid
#                                               | DTDP          = ADCIRC time step
#                                               | NSPOOLGE      = Num Timesteps in which info is writen to fort.63
#                                               | IRTYPE        = Record Type
# TIME, IT                                      | TIME          = Model time
#                                               | IT            = Time step num since beginnig of the run
# k=1 to NP
#   k, ETA2(k)                                  | ETA2          = Surface elevation at current time step
#


def read_fort63(filename):
    logging.info('Reading in data from fort.63 file...')

    with open(filename) as fort63:
        (_, _, _) = fort63.readline().split()

        (num_datasets, num_nodes, _, _, _, _, _) = fort63.readline().split()

        num_datasets = int(num_datasets)
        num_nodes = int(num_nodes)

        vector_data = np.zeros((num_datasets, num_nodes, 1))

        logging.debug(
            'Reading in %i sets of %i nodes' %
            (num_datasets, num_nodes))

        # Weird bug...
        for dataset in range(num_datasets - 3):
            (_, _) = fort63.readline().split()

            for node in range(num_nodes):
                (_, height) = [float(s) for s in fort63.readline().split()]
                vector_data[dataset][node] = height

        logging.debug('Done reading!')
        logging.debug("Here's a peek into the data: {}".format(vector_data))

        return vector_data
