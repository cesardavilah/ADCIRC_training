import logging
import numpy as np

def read_fort13(filename):
    """
    Read in fort.13...
    """
    logging.info('Reading in data from fort.13...')
    with open(filename) as fort13:
        
        # Parse header data
        _ = fort13.readline()
        
        num_nodes = int(fort13.readline())
        num_attr = int(fort13.readline())
        
        attr_metadata = {}
        # Parse in attr data
        for attr in range(num_attr):
            attr_name = fort13.readline().strip()
            units = fort13.readline().strip()
            values_per_node = int(fort13.readline())
            default_values = fort13.readline().split()
            attr_metadata[attr_name] = (units, values_per_node, default_values)

        for attr in range(num_attr):
            attr_name = fort13.readline().strip()
            num_nodes_not_default = int(fort13.readline())
            
            attr_data = np.full((num_nodes, 1), attr_metadata[attr_name][2][0])
            
            for node in range(num_nodes_not_default):
                node_data = fort13.readline().split()
                
                # Temp hack
                node_num = int(node_data[0])
                attributes = float(node_data[1])
                
                attr_data[node_num-1] = attributes
            
            logging.debug("Here's a look into the data: {}".format(attr_data))
            
            return attr_data 
