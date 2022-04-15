# import os
# import os
# import iris_grib
#
# cubes = iris_grib.load_cubes("ds.wdir.bin")
# cubes = list(cubes)
#
#
# print(cubes)
import pygrib
import re
# import pyqtgraph as pg
import numpy as np

# import simplekml
import csv
import numpy as np

import math





def ndfd_open(filepath):
    '''
    Opens a windspeed or winddirection grib file from ndfd(ar.oceanic)
    :param filepath: Specifies the location of the grib file
    :return: Returns a pygrib object with the grib file open
    '''
    grib = pygrib.open(filepath)
    return grib

def ndfd_inventory_print_all(gribfile):
    '''
    Prints all the tables inside a ndfd(ar.oceanic) windspeed or winddirection grib file
    :param gribfile: Needs to provide an open grib file (pygrib) object
    :return: Void. Prints to screen all the available grid tables.
    '''
    gribfile.seek(0)
    for grb in gribfile:
        print(grb)

def ndfd_about(gribfile, which: int = -1):
    for line in gribfile:
        print(line)


def ndfd_inventory_picker(gribfile, hstart: int, hend: int):
    '''
    Returns grib tables from a raw grib file according to forecast constraint. From hourstart to hourend.
    :param gribfile: Needs to provide an open grib file (pygrib) object
    :param hstart: Desired start hour of forecast
    :param hend: Desired end hour of forecast
    :return: List. List of grib tables in the range hstart - hend specified.
    '''
    rxdict = {
        # 'startdate': re.compile(r'.*from \d*'),  # Starting date
        'hour': re.compile(r'.*fcst time (?P<hour>\d*) hrs')  # Hour picker
    }

    def parse(line):
        for key, rx in rxdict.items():
            match = rx.search(line)
            if match:
                return key, match
        return None, None


    #TODO Pick grids from forecast range
    if (hstart <= 0):
        return None
    else:
        selectedgribs = []
        gribfile.seek(0)
        for grb in gribfile:
            # print(str(grb))
            key, match = parse(str(grb))
            if key == 'hour':
                # print(match.group('hour'))
                if hstart <= int(match.group('hour')) <= hend:
                    # print(match.group('hour'))
                    selectedgribs.append(grb)
    return selectedgribs

def extract_coords(gribfile):
    '''
    Extracts the lats and lons of a gribfile specified.
    :param gribfile: Needs to provide an open grib file (pygrib) object
    :return: Tuple (lats, lons). Retuns a list of lats and lons.
    '''
    return gribfile.select()[0].latlons()


def merge_lats_lons(lats, lons):
    merged = []
    if (lats.shape == lons.shape):
        x, y = lats.shape
        # for i in range(0, y):
        #     print(lats[0][i])
        for j in range(y):
            for i in range(x):
                # print(str(lats[i][j]) + ' ' + str(lons[i][j]))
                if ((16 <= lats[i][j] <= 32) and (-101 <= lons[i][j] <= -76)):
                    merged.append([lons[i][j], lats[i][j]])
        return merged
    else:
        return None

def full_lats_lons_data_values(grb, lat1, lat2, lon1, lon2):

    data, lats, lons = grb.data(lat1, lat2, lon1, lon2)
    merge = []

    for x in range(len(lats)):
        merge.append([lats[x], lons[x], data[x]])
    return merge


def plot(merged):
    import sys

    # Set white background and black foreground
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')

    # Generate random points
    n = 1000
    print('Number of points: ' + str(n))
    data = np.random.normal(size=(2, n))
    # print(data)

    # Create the main application instance
    app = pg.mkQApp()

    # Create the view
    view = pg.PlotWidget()
    view.resize(800, 600)
    view.setWindowTitle('Scatter plot using pyqtgraph with PyQT5')
    view.setAspectLocked(True)
    view.show()

    # Create the scatter plot and add it to the view
    scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color='r'), symbol='o', size=1)
    # scatter2 = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color='b'), symbol='o', size=1)
    view.addItem(scatter)

    # Convert data array into a list of dictionaries with the x,y-coordinates
    # pos = {'pos': [1, 1]}
    pos = []
    for coord in merged:
        pos.append({'pos': [coord[1], coord[0]]})

    # pos.append({'pos': [-74.006, 40.71]})
    # pos = [{'pos': [1, 1]}, {'pos': [2, 2]}]
    # pos = [{'pos': data[:, i]} for i in range(n)]

    # print(pos)

    now = pg.ptime.time()
    scatter.setData(pos)
    # scatter2.setData(mexico)
    print("Plot time: {} sec".format(pg.ptime.time() - now))

    # Gracefully exit the application
    sys.exit(app.exec_())

def to_vector(wspeed, wdirection):
    '''
    Turns VECTOR wind speed and wind direction into u (x) and v (y) components.
    :param wspeed: Wind speed number in m/s
    :param wdirection: Wind direction number in degrees 0-360
    :return: Tuple (vx, vy). Returns each component value.
    '''
    vx = wspeed*math.cos(math.radians(wdirection))
    vy = wspeed*math.sin(math.radians(wdirection))
    return vx, vy

def extract_raw_spd_dir(hstart, hend, lat1, lat2, lon1, lon2):
    '''
    Extracts latitude, longitude, windspeed, winddirection of each grib table form forecast
    hstart to hend in a grid inside lat1 lat2 lon1 lon2
    :param hstart: Forecast hour start
    :param hend: Forecast hour end
    :param lat1: Min lat to include
    :param lat2: Max lat to include
    :param lon1: Min lon to include
    :param lon2: Max lon to include
    :return:
    '''
    wspd = ndfd_open('./RawData/NDFD/ds.wspd.bin')
    wspd.seek(0)
    selectedgribs = ndfd_inventory_picker(wspd, hstart, hend) #38
    # print(selectedgribs)
    dataextractwspd = []
    for grb in selectedgribs:
        print(grb)
        dataextractwspd.append(full_lats_lons_data_values(grb, lat1, lat2, lon1, lon2))

    # #Wind Direction
    wdir = ndfd_open('./RawData/NDFD/ds.wdir.bin')
    wdir.seek(0)
    # for grb in wdir:
    #     print(grb)
    selectedgribs2 = ndfd_inventory_picker(wdir, hstart, hend)
    # print(selectedgribs2)
    dataextractwdir = []
    for grb in selectedgribs2:
        print(grb)
        dataextractwdir.append(full_lats_lons_data_values(grb, lat1, lat2, lon1, lon2))

    return dataextractwspd, dataextractwdir

def create_components(wspd, wdir):
    if (len(wspd) == len(wspd)):
        windcomponents = []
        for i in range(len(wspd)):
            x, y = to_vector(wspd[i][2], wdir[i][2])
            # print(x, y)
            windcomponents.append([wspd[i][0], wspd[i][1], x, y])
        return windcomponents
    else:
        print("Length of wspd and wdir doesn't match")
        return None


def whatever():

    wspd = ndfd_open('./RawData/NDFD/ds.wspd.bin')
    wdir = ndfd_open('./RawData/NDFD/ds.wdir.bin')
    #
    # wspd.seek(0)
    # grb = wspd.message(1)
    # lats, lons = grb.latlons()
    # print(lats.shape, lats.min(), lats.max())
    #
    #
    # data, lats, lons = grb.data(lat1=16, lat2=32, lon1=-101, lon2=-76)
    #
    # print(lats.shape, lats.min(), lats.max())
    # print(lons.shape, lons.min(), lons.max())
    #
    # counter = 1
    # linescounter = 0


    # counter = 0
    # for i in range(len(lats)):
    #     if lats[i] != lats[i-1]:
    #         print(lats[i], lats[i-1],lats[i] - lats[i-1])
    #     # print(lats[i])
    # print(counter)


    # counter = 0
    # for i in range(len(lons)):
    #     print(lons[i])
        # if lons[i] == -76.00240837440381:
        #     counter += 1
        #     print(lons[i])
    # # print(counter)
    #
    # counter = 0
    # for i in range(len(lons)):
    #     print(lons[i], lons[i-1], lons[i] - lons[i-1])
    # #

    # print(lons[:524])
    # for i in range(len(lons)):
    #
    #     print(counter, lons[i] - lons[i-1])
    #     counter += 1
    #     if (lons[i] - lons[i-1] < 0):
    #         print(counter)
    #         linescounter+= 1
    #         counter = 1

    # print(linescounter)
    # print(counter)

    #
    # for row in lats:
    #     print(row)

    # grb = wspd
    # grb = wspd.select(name='10 metre wind speed')[0]
    # lats, lons = extract_coords(grb)












    #START OR ROUTINE
    print(ndfd_about(wspd))
    print(ndfd_about(wdir))

    # wspd, wdir = extract_raw_spd_dir(1, 69, lat1=16, lat2=32, lon1=-101, lon2=-50)

    wspd, wdir = extract_raw_spd_dir(1, 18, lat1=16, lat2=32, lon1=-101, lon2=-76)
    # wspd, wdir = extract_raw_spd_dir(1, 3, lat1=16, lat2=32, lon1=-101, lon2=-76)


    components = []
    for i in range(len(wspd)):
        components.append(create_components(wspd[i], wdir[i]))

    #Identifying what the size of the separation bewteen longitudes is
    for comp in components:
        for i in range(len(comp)):
            if (comp[i][1] - comp[i-1][1] <= 0 ):
                print(comp[i])
                print(comp[i-1])
                print(comp[i][1] - comp[i-1][1])
            # print(row)
            # print(row[1] - row[1])

    # for component in components:
    #     component = component[:59818]
    #     print(len(component))
    #     for i in range(0, 59818):
    #         component[i] = component[i][2:]
    #         component[i].append(10.33)
    #         component[i].insert(0, i+1)
    #         print(component[i])

    # Turning into FORT.22 format (handling masks)
    for comp in range(len(components)):
        components[comp] = components[comp][:47946]
        for row in range(len(components[comp])):
            components[comp][row] = components[comp][row][2:]
            components[comp][row].append(6.33)
            components[comp][row].insert(0, row+1)
            if (np.ma.is_masked(components[comp][row][1])):
                components[comp][row][1] = 0
            if (np.ma.is_masked(components[comp][row][2])):
                components[comp][row][2] = 0
            components[comp][row][1] = components[comp][row][1] * 5
            components[comp][row][2] = components[comp][row][2] * 5
            components[comp][row][3] = components[comp][row][3] * 5
            # print(components[comp][row])

    with open('fort.22', mode='w', newline='') as file:
        towrite: str = ''
        for component in components:
            for row in component:
                # print(row)
                # towrite += '%s %.6f %.6f %.6f\n' % (row[0], row[1], row[2], row[3])
                towrite += '%.6f %.6f %.6f\n' % (row[1], row[2], row[3])
        file.write(towrite)







# whatever()







        # for row in component:
        #     row = row[2:]
        #     row.append(10.33)
        #     print(row)


    # for node in range(1, 59819):



    #
    # windcomponents = create_components(wspd, wdir)
    #
    # print(len(wspd[0]))


    #Hour produ



    # for row in wspd[0]:
    #     # print(row)
    #     if (np.ma.is_masked(row[2])):
    #         row[2] = 0
    #         print(row)
    # print(len(wspd[0]))
    # print(len(wdir[0]))

    # wdirgrb = wdir.select(name='10 metre wind direction')[0]

    # merge = full_lats_lons_data_values(grb, lat1=16, lat2=32, lon1=-101, lon2=-76)
    # plot(merge)


    # grb = wspd.message(1)
    #
    # data, lats, lons = grb.data()
    #
    # print(data)

    # for d in data:
    #     print(len(d))


    # print(data[0][0], lats[0][0], lons[0][0])
    #
    # print(data.shape, lats.shape, lons.shape)

    # merge = full_lats_lons_data_values(grb, lat1=16, lat2=32, lon1=-101, lon2=-76)








    # ndfd_about(wspd)
    # selected = ndfd_inventory_picker(wspd, 3, 6)
    #
    # lats, lons = extract_coords(wspd)
    #
    # print(lats.shape)
    #
    # counter = 0
    # for lat in lats:
    #     counter += 1
    #     # print(lat.shape)
    #
    #
    # ls = []
    # for i in range(lats.shape[1]):
    #     ls.append([lons[0][i], lats[0][i]])
    #
    # # merged = merge_lats_lons(lats, lons)
    # # plot(merged)
    #
    # valueswspd = wspd.select(name='10 metre wind speed')[0].values
    #
    # data, lats, lons = valueswspd.data(lat1=16, lat2=32, lon1=-101, lon2=-76)
    #
    #
    # fulldata = full_data_lats_lons_values(valueswspd)
    #




    # print(valueswspd.shape)



    # print(valueswspd.values)


    # print(len(valueswspd))

    # for value in valueswspd.values:
    #     for v in value:
    #         print(v)
    #     # print(value)
    # print(valueswspd.values)

    # print(lats[0][0])
    # print(lats[1])
    # print(counter)


    # merged = merge_lats_lons(lats, lons)
    # print(merged)

    # plot(merged)






    #
    # wspd = pygrib.open('./RawData/NDFD/ds.wspd.bin')
    # wdir = pygrib.open('./RawData/NDFD/ds.wdir.bin')
    # #
    # # grbs.seek(0)
    # ndfd_inventory_print_all(wspd)
    # # grbwspd = wspd.select(name='10 metre wind speed')[1]
    # grbwspd = wspd.select()[0]
    # grbwdir = wdir.select(name='10 metre wind direction')[0]
    # #
    # print(grbwspd)

    # print(grbwspd.values)

    # lats, lons = grbwspd.latlons()
    # spdvals = grbwspd.values
    # dirvals = grbwdir.values
    # nrows = lats.shape[0]
    # ncols = lats.shape[1]
    # print(spdvals.shape)
    # print(lats.shape)
    # print(lons.shape)
    # totalpoints = 2953665
    # print(lats)

    #
    # with open('data1.csv', 'w') as csvfile:
    #     filewriter = csv.writer(csvfile, delimiter=',',
    #                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     filewriter.writerow(['Latitude', 'Longitude', 'WindSpeed', "WindDirection"])
    #     for j in range(ncols):
    #         for i in range(nrows):
    #             if (lats[i][j] >=25.26 and lats[i][j] <= 27.29 and lons[i][j] >= -100 and lons[i][j] <= -96):
    #                 filewriter.writerow([str(lats[i][j]), str(lons[i][j]), str(spdvals[i][j]), str(dirvals[i][j])])
    #             # print(str(lats[i][j]) +" "+ str(lons[i][j]))


    # dataset = Dataset('datatest.nc', 'w', format='NETCDF4_CLASSIC')
    # lat_dim = dataset.createDimension('lat', totalpoints)
    # lon_dim = dataset.createDimension('lon', totalpoints)
    # wind_spd = dataset.createDimension('spd', totalpoints)
    # time_dim = dataset.createDimension('time', None)
    #
    # lat = dataset.createVariable('lat', np.float32, ('lat',))
    # lat.long_name = 'latitude'
    # lon = dataset.createVariable('lon', np.float32, ('lon',))
    # lon.long_name = 'longitude'
    # time = dataset.createVariable('time', np.float64, ('time',))
    # time.units = '1 hours since 201904010400'
    # time.long_name = 'time'
    #
    # wind_spd = dataset.createVariable('spd', np.float32, ('time','lat','lon'))
    # wind_spd.units = r'm s**-1'
    # wind_spd.standard_name = 'wind_speed'
    # print(wind_spd)
    #
    # latsone = lats.ravel()
    # lonsone = lons.ravel()
    # lat[:] = latsone
    # lon[:] = lonsone
    # wind_spd = spdvals.ravel()
    #
    # dataset.close()


    #
    # print(lats)
    # print(nrows)
    # print(ncols)
    # print(lats[row][column])


    # kml = simplekml.Kml()
    # pnt = kml.newpoint()

            # print(str(lats[i][j])+" "+str(lons[i][j]))

    # kml.save('points.kml')