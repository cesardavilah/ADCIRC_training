import logging
import numpy as np

# Read FORT.74 file (v53)
# -----------------------
# RUNDES, RUNID, AGRID                          | RUNDES, RUNID = Run Descriptions 1 & 2    | ARGID = Grid identifier(IDENT)
# NDSETSW, NP, DTDP*NSPOOLGW, NSPOOLGW, IRTYPE  | NDSETSW       = Num datasets to be spooled to fort {73,74}
#                                               | NP            = Num nodes in horiz grid
#                                               | DTDP          = ADCIRC time step: (< 0 Predictor is used | > 0 Predictor is not used)
#                                               | NSPOOLGW      = Num Timesteps in which info is written to fort {73,74}
#                                               | IRTYPE        = Record Type (=1 elevation, =2 velocity, =3 3D velocity)
# TIME, IT                                      | TIME          = Model time
#                                              time_slice | IT = Time step number since beginning of run
# k=1 to NP                                     | NP            = Num elements in horiz grid
#   k, WVNXOUT(k), WVNYOUT(k)                   | WVN{X,Y}OUT   = Depends heavily on what's defined in FORT.15 (NWS, ICS, G)
#                                               |               Refer to documentation for more advice...
#                                               |               https://adcirc.org/home/documentation/users-manual-v53/parameter-definitions/#WVNXOUT_WVNYOUT
#


def read_fort74(filename, time_slice):
    logging.info('Reading in data from fort.74...')

    with open(filename) as fort74:
        (_, _, _) = fort74.readline().split()

        (num_datasets, num_nodes, _, _, _, _, _) = fort74.readline().split()

        num_datasets = int(num_datasets)
        num_nodes = int(num_nodes)

        vector_data = np.zeros((num_nodes, 2))

        if time_slice >= num_datasets:
            logging.error('Time slice %i is out of bounds! %i is the limit!' % (time_slice, num_datasets-1))
            raise IndexError

        # Skip other timeslices
        for skipped_slice in range(time_slice):
            fort74.readline()
            
            for skipped_node in range(num_nodes):
                fort74.readline()

        # Read required timeslice 
        (_, _) = fort74.readline().split()

        for node in range(num_nodes):
            (_, x, y) = [float(s) for s in fort74.readline().split()]
            vector_data[node] = [x, y]

        logging.debug('Done reading!')
        logging.debug("Here's a peek into the data: {}".format(vector_data))

        return vector_data
