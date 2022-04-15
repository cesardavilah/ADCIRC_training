import logging
import numpy as np

# Read FORT.14 file (v53)
# -----------------------
# IDENT
# NE, NP                                        | NE            = Num elements in horiz grid
#                                               | NP            = Num nodes in horiz grid
# k=1 to NP
#   JN, x, y, z                                 | JN            = Node Num
#
# k=1 to NE
#   JE, NHY(ONLY NUM 3), JE1, JE2, JE3          | JE            = Elem num, The ElemNum[1-3] forms a triangle, represeting the group(?)
#
# NOPE                                          | NOPE          = Num elevation boundary segs
# NETA                                          | NETA          = Num elev bound nodes
#
# for k=1 to NOPE
#   KVDLL(k), IBTYPEE(k)(ONLY NUM 0)            | KVDLL         = Num nodes in elevation boundary segment
#                                               | IBTYPEE       = Elevation boundary type, surrently specified in FORT.15 || FORT.19
#   for j=1 to NVDLL(k)
#       NBDV(k,j)                               | NBDV          = Node nums on specified boundary seg
#
# NBOU                                          | NBOU          =
# NVEL                                          | NVEL          =
#
# for k=1 to NBOU
#   NVELL(k), IBTYPE(k)                         | NVELL         =
#                                               | IBTYPE        =
#
#   for j=1 to NVELL(k)
#


def read_fort14(filename):
    """
    Read in fort14 file.
    Constructs an object out of the recived data(?)
    """
    logging.info('Reading in data from fort.14...')

    with open(filename) as fort14:
        _ = fort14.readline()
        (num_edges, num_nodes) = [int(s) for s in fort14.readline().split()]

        node_array = np.zeros((num_nodes, 3))

        logging.debug('Reading %i nodes...' % (num_nodes))

        for node in range(num_nodes):
            (_, x, y, z) = [float(s) for s in fort14.readline().split()]
            node_array[node] = [x, y, z]

        triangle_data = np.zeros((num_edges, 3))
        
        for triangle in range(num_edges):
            (_, _, node1, node2, node3) = [int(s) for s in fort14.readline().split()]
            triangle_data[triangle] = [node1-1, node2-1, node3-1]

        logging.debug('Done reading!')
        logging.debug("Here's a peek into the data: {}".format(node_array))
        logging.debug("Here's a peek into the triangle dtime_sliceata: {}".format(triangle))

        return (node_array, triangle_data)
