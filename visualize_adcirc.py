import logging
import os
import sys
import numpy as np

from fortreader import fort74, fort73, fort64, fort63, fort22, fort14, fort13, cesar_fort22

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

if __name__ == '__main__':

    if len(sys.argv) > 4 or len(sys.argv) < 4:
        print('Usage: %s dir timeSlice' % (sys.argv[0]))
        print('-' * 80)
        print('dir       : Searches for fort 14, 63, 64, 73, and 74 in the specified directory')
        print('timeSlice : Sets slice to use for fort 63, 64, 73, 74')
        print('toggleBit : Set to 0 if sara, 1 if cesar')
        exit(-1)

    forts_dir = os.path.join('.', sys.argv[1])
    time_slice = int(sys.argv[2])
    toggle_bit = int(sys.argv[3])

    # Hacky Solution for now
    wind_velocity = wind_pressure = wave_velocity = waves_array = hurricane_data = hurricane_course = nodal_attr = node_array = triangles = None

    # wind_velocity = fort74.read_fort74(os.path.join(forts_dir, 'fort.74'), time_slice)
    #wind_pressure = fort73.read_fort73(os.path.join(forts_dir, 'fort.73'), time_slice)
    #wave_velocity = fort64.read_fort64(os.path.join(forts_dir, 'fort.64'))
    waves_array = fort63.read_fort63(os.path.join(forts_dir, 'fort.63'))

    if toggle_bit == 0:
        hurricane_course = fort22.read_fort22(
            os.path.join(forts_dir, 'fort.22'))
    elif toggle_bit == 1:
        hurricane_data = cesar_fort22.read_fort22_cesar(
            os.path.join(forts_dir, 'fort.22'), time_slice)
    else:
        logging.warning('Toggle bit not 0 or 1! Ignoring fort.22...')

    nodal_attr = fort13.read_fort13(os.path.join(forts_dir, 'fort.13'))

    (node_array, triangles) = fort14.read_fort14(
        os.path.join(forts_dir, 'fort.14'))

    # Create xyz file
    # if node_array is not None:
    #     logging.info('Creating fort14.xyz...')

    #     with open('fort14.xyz', 'w') as xyz:
    #         for node in node_array:
    #             (x, y, z) = node
    #             xyz.write('{} {} {}\n'.format(x, y, -z))

    if node_array is not None and waves_array is not None:
        logging.info('Creating fort63.xyz...')

        with open('fort63.xyz', 'w') as xyz:
            node_coords = np.delete(node_array, 2, 1)
            node_waves = np.hstack((node_coords, waves_array[time_slice]))
            for (x, y, z) in node_waves:
                xyz.write('{} {} {}\n'.format(x, y, z))

    # if node_array is not None and wave_velocity is not None:
    #     logging.info('Creating fort64-x.xyz...')

    #     with open('fort64-x.xyz', 'w') as xyz:
    #         node_coords = np.delete(node_array, 2, 1)
    #         wave_vel_x = np.delete(wave_velocity, 1, 2)
    #         node_vector = np.hstack((node_coords, wave_vel_x[time_slice]))
    #         for (x, y, z) in node_vector:
    #             xyz.write('{} {} {}\n'.format(x, y, z))

    #     logging.info('Creating fort64-y.xyz...')

    #     with open('fort64-y.xyz', 'w') as xyz:
    #         node_coords = np.delete(node_array, 2, 1)
    #         wave_vel_y = np.delete(wave_velocity, 0, 2)
    #         node_vector = np.hstack((node_coords, wave_vel_y[time_slice]))
    #         for (x, y, z) in node_vector:
    #             xyz.write('{} {} {}\n'.format(x, y, z))

    # if node_array is not None and wind_pressure is not None:
    #     logging.info('Creating fort73.xyz...')

    #     with open('fort73.xyz', 'w') as xyz:
    #         node_coords = np.delete(node_array, 2, 1)
    #         node_pressure = np.hstack((node_coords, wind_pressure))
    #         for (x, y, z) in node_pressure:
    #             xyz.write('{} {} {}\n'.format(x, y, z))

    # if node_array is not None and wind_velocity is not None:
    #     logging.info('Creating fort74-x.xyz...')

    #     with open('fort74-x.xyz', 'w') as xyz:
    #         node_coords = np.delete(node_array, 2, 1)
    #         wind_vel_x = np.delete(wind_velocity, 1, 1)
    #         node_vector = np.hstack((node_coords, wind_vel_x))
    #         for (x, y, z) in node_vector:
    #             xyz.write('{} {} {}\n'.format(x, y, z))

    #     logging.info('Creating fort74-y.xyz...')

    #     with open('fort74-y.xyz', 'w') as xyz:
    #         node_coords = np.delete(node_array, 2, 1)
    #         wind_vel_y = np.delete(wind_velocity, 0, 1)
    #         node_vector = np.hstack((node_coords, wind_vel_y))
    #         for (x, y, z) in node_vector:
    #             xyz.write('{} {} {}\n'.format(x, y, z))

    # if node_array is not None and triangles is not None:
    #     logging.info('Creating triangle-lines.xyz...')
    #     with open('triangle-lines.xy', 'w') as xyz:
    #         for (x, y, z) in triangles:
    #             x = int(x)
    #             y = int(y)
    #             z = int(z)

    #             xyz.write('> Edge {}-{}\n'.format(x, y))
    #             xyz.write('{}  {}\n'.format(
    #                 node_array[x][0], node_array[x][1]))
    #             xyz.write('{}  {}\n'.format(
    #                 node_array[y][0], node_array[y][1]))

    #             xyz.write('> Edge {}-{}\n'.format(y, z))
    #             xyz.write('{}  {}\n'.format(
    #                 node_array[y][0], node_array[y][1]))
    #             xyz.write('{}  {}\n'.format(
    #                 node_array[z][0], node_array[z][1]))

    #             xyz.write('> Edge {}-{}\n'.format(z, x))
    #             xyz.write('{}  {}\n'.format(
    #                 node_array[z][0], node_array[z][1]))
    #             xyz.write('{}  {}\n'.format(
    #                 node_array[x][0], node_array[x][1]))

    # if triangles is not None:
    #     logging.info('Creating triangle.xyz...')

    #     with open('triangle.xyz', 'w') as xyz:
    #         for (x, y, z) in triangles:
    #             xyz.write('{} {} {}\n'.format(x, y, z))

    # if hurricane_data is not None:
    #     logging.info('Creating hurricane_plot.plt...')

    #     with open('hurricane_plot.plt', 'w') as plot:
    #         for grid_x in range(280):
    #             for grid_y in range(500):
    #                 (lon, lat, theta, length) = hurricane_data[grid_x][grid_y]
    #                 plot.write('{} {} {} {}\n'.format(lon, lat, theta, length))

    # if hurricane_course is not None:
    #     logging.info('Creating hurricane_course.xy...')

    #     with open('hurricane_course.xy', 'w') as xy:
    #         for (lon, lat) in hurricane_course:
    #             xy.write('{} {}\n'.format(lon, lat))

    # if node_array is not None and nodal_attr is not None:
    #     logging.info('Creating fort13.xyz...')

    #     with open('fort13.xyz', 'w') as xyz:
    #         node_coords = np.delete(node_array, 2, 1)
    #         node_attrs = np.hstack((node_coords, nodal_attr))
    #         for (x, y, z) in node_attrs:
    #             xyz.write('{} {} {}\n'.format(x, y, z))

    # Generate GeoJSON of data
    # from io import StringIO
    # from shutil import copyfileobj

    # if node_array is not None and waves_array is not None and triangles is not None:
    #     logging.info('Creating wave-height.geojson...')

    #     node_coords = np.delete(node_array, 2, 1)
    #     node_waves = np.hstack((node_coords, waves_array[time_slice]))

        # Create GeoJSON start
        # geojson = StringIO()
        # geojson.write('{"type":"FeatureCollection","features":[')

        # Generate Coordinate array first!
        # for (x, y, z) in triangles:
            # Begin feature
            # geojson.write('{"type":"Feature","geometry":{"type":"Polygon","coordinates":[')

            # XYZ are 1 indexed, arrays are 0!
            # x = int(x)
            # y = int(y)
            # z = int(z)

            # Assume coords are right-hand ordered
            # geojson.write('[[{lon1},{lat1}],[{lon2},{lat2}],[{lon3},{lat3}],[{lon1},{lat1}]]]}},'.format(
            #     lon1=node_array[x][0], lat1=node_array[x][1], lon2=node_array[y][0], lat2=node_array[y][1], lon3=node_array[z][0], lat3=node_array[z][1]))

            # Write node metadata
            # avg = []
            # for i in range(400):
            # node_waves = np.hstack((node_coords, waves_array[i]))
            # x_height = node_waves[x][2]
            # y_height = node_waves[y][2]
            # z_height = node_waves[z][2]

            # avg = (x_height + y_height + z_height) / 3

            # geojson.write('"properties":{{"avg z":{avg} }}'.format(avg=avg))

            # End feature
            # geojson.write('},')

        # End GeoJSON object
        # geojson.seek(geojson.tell()-1)  # Seek to write over last comma
        # geojson.write(']}')

        # Write GeoJSON object
        # with open('wave-height.geojson', 'w') as geofile:
        #     geojson.seek(0)
        #     copyfileobj(geojson, geofile)

        # No idea if this works
        # with open('wave-height-corr.geojson', 'w') as geofile:
        #     from geojson_rewind import rewind
        #     res = rewind(geojson.getvalue())
        #     geofile.write(res)


    logging.info('Done!')
