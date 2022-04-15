import parsegrib as pgrib
# import pygrib
import importlib
import numpy as np

import matplotlib.pyplot as plt
from scipy.interpolate import griddata

import pyqtgraph as pg

from datetime import datetime


def merge_lats_lons(lats, lons):
    merged = []
    if (lats.shape == lons.shape):
        x, y = lats.shape
        # for i in range(0, y):
        #     print(lats[0][i])
        for j in range(y):
            for i in range(x):
                # print(str(lats[i][j]) + ' ' + str(lons[i][j]))
                if ((18 <= lats[i][j] <= 32) and (-101 <= lons[i][j] <= -76)):
                    merged.append([lons[i][j], lats[i][j]])
        return merged
    else:
        return None


# def plot(merged):
#     import sys
#
#     # Set white background and black foreground
#     pg.setConfigOption('background', 'w')
#     pg.setConfigOption('foreground', 'k')
#
#     # Generate random points
#     n = 1000
#     print('Number of points: ' + str(n))
#     data = np.random.normal(size=(2, n))
#     # print(data)
#
#     # Create the main application instance
#     app = pg.mkQApp()
#
#     # Create the view
#     view = pg.PlotWidget()
#     view.resize(800, 600)
#     view.setWindowTitle('Scatter plot using pyqtgraph with PyQT5')
#     view.setAspectLocked(True)
#     view.show()
#
#     # Create the scatter plot and add it to the view
#     scatter = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color='r'), symbol='o', size=1)
#     # scatter2 = pg.ScatterPlotItem(pen=pg.mkPen(width=5, color='b'), symbol='o', size=1)
#     view.addItem(scatter)
#
#     # Convert data array into a list of dictionaries with the x,y-coordinates
#     # pos = {'pos': [1, 1]}
#     pos = []
#     for coord in merged:
#         pos.append({'pos': [coord[1], coord[0]]})
#
#     # pos.append({'pos': [-74.006, 40.71]})
#     # pos = [{'pos': [1, 1]}, {'pos': [2, 2]}]
#     # pos = [{'pos': data[:, i]} for i in range(n)]
#
#     # print(pos)
#
#     now = pg.ptime.time()
#     scatter.setData(pos)
#     # scatter2.setData(mexico)
#     print("Plot time: {} sec".format(pg.ptime.time() - now))
#
#     # Gracefully exit the application
#     sys.exit(app.exec_())

# def ext/ract_nws(nam):

def print_nam(nam):
    naminfo = nam.select()[8], nam.select()[9], nam.select()[2]
    ucomp, lats, lons = naminfo[0].data(lat1=18, lat2=32, lon1=-101, lon2=-76)
    print(naminfo[0])

def extract_nam(nam):
    '''
    :param nam: An opened nam grb at a certain time.
    :return: Returns a merged list with ucomp, vcomp and press at a certan time (of nam grib).
    '''
    # naminfo = nam.select()[8], nam.select()[9], nam.select()[2]
    # naminfo = nam.select()[7], nam.select()[8], nam.select()[336]
    # naminfo = nam.select()[7], nam.select()[8], nam.select()[2] #FOR GRIB FILES (EMILY)
    naminfo = nam.select(name='10 metre U wind component')[0], nam.select(name='10 metre V wind component')[0], \
              nam.select(name='Surface pressure')[0]

    print(naminfo)

    ucomp, lats, lons = naminfo[0].data(lat1=18, lat2=32, lon1=-101, lon2=-76)
    # print(naminfo[0], ucomp.shape, lats.shape, lons.shape)
    # ucomp, lats, lons = ucomp[:26441], lats[:26441], lons[:26441]
    # print(ucomp.shape)

    vcomp, lats, lons = naminfo[1].data(lat1=18, lat2=32, lon1=-101, lon2=-76)
    # print(naminfo[1], vcomp.shape, lats.shape, lons.shape)
    # vcomp = vcomp[:26441]

    press, lats, lons = naminfo[2].data(lat1=18, lat2=32, lon1=-101, lon2=-76)
    # press = press[:26441]

    merged = []
    merged.append(ucomp)
    merged.append(vcomp)
    merged.append(press)
    # for i in range(len(ucomp)):
    #     merged.append([ucomp[i], vcomp[i], press[i]])
    return merged

def grab_fcst(date, forecast_production_hr, path, extension):
    result = []
    # namlocation = '/home/cesar/Documents/NAM/NAM20080722/nam_218_20080722_0000_000.grb2'
    # namlocation = '/home/cesar/Documents/NAM/nam20080720/nam_218_20080720_0000_000.grb2'
    # namlocation = '/media/cesar/extra/nam_218_20080712_0000_000.grb2'
    # namlocation = '/media/cesar/extra/nam_218_20100621_0000_000.grb2'
    # namlocation = '/home/cesar/Desktop/NAM/emily_15days/extracteddataemily/nam_218_20050709_0000_001.grib'
    # namlocation = '/home/cesar/Desktop/NAM/emily_15days/extractederin/nam_218_20070810_0000_001.grib'
    # namlocation = '/media/cesar/Elements/RAWDATA/3months20080720-20081020/nam_218_20080720_0000_000.grb2'
    # namlocation = '/home/cesar/RAWDATA/nam_218_20080720_0000_000.grb2'
    # namlocation = '/home/cesar/RAWDATA/JULY2020/nam_218_20200722_0000_000.grb2'
    # namlocation = '/media/sf_SHARED_FOLDER_VIRTUALBOX/2018_hurricane_season/grbs/nam_218_20180601_0000_000.grb2'

    filename = '/home/cesar/Desktop/NAM/nam_218_'

    # path = '/media/sf_SHARED_FOLDER_VIRTUALBOX/2018_hurricane_season/grbs/'

    # extension = '.grib2'

    # start = datetime.strptime(startdate, "%Y%m%d%H")
    # stop = datetime.strptime(enddate, "%Y%m%d%H")

    # nam = pgrib.ndfd_open('/home/cesar/Documents/NAM/nam_218_20080723_0000_000.grb2')
    nam = pgrib.ndfd_open(path+file_single_84(date, forecast_production_hr=forecast_production_hr, extension=extension))

    # naminfo = nam.select()
    # naminfo = nam.select()[7], nam.select()[8], nam.select()[336] #FOR MODERN GRIB2 2020L
    naminfo = nam.select(name='10 metre U wind component')[0], nam.select(name='10 metre V wind component')[0], nam.select(name='Surface pressure')[0]  # FOR MODERN GRIB2 2020L
    # naminfo = nam.select()[8], nam.select()[9], nam.select()[2]
    print(naminfo)

    # naminfo = nam.select()[7], nam.select()[8], nam.select()[2] #FOR GRIB FILES (EMILY)
    # print(naminfo)

    ucomponent = naminfo[0]

    ucomp, lats, lons = ucomponent.data(lat1=18, lat2=32, lon1=-101, lon2=-76)

    # ATTENTION
    # if data is sequential and not combining several days from different datasets, set sequential to true
    # sequential = True
    # t_start = start


    for file in file_generator_84(date, forecast_production_hr='00', extension=extension):
        nam = pgrib.ndfd_open(path + file)

        plotname = file

        # print('EXTRACTING /home/cesar/Documents/NAM/nam_218_20080723_0000_' + str(hour) + '.grb2')
        print('EXTRACTING ' + file)
        # print('EXTRACTING '+namlocation[:-8] + str(hour) + '.grib') #FOR GRIB FILES (EMILY)
        extract = extract_nam(nam)
        # print('INTERPOLATING /home/cesar/Documents/NAM/nam_218_20080723_0000_' + str(hour) + '.grb2')
        print('INTERPOLATING ' + file)
        # print('INTERPOLATING ' + namlocation[:-8] + str(hour) + '.grib') #FOR GRIB FILES (EMILY)

        interpolated = interpolate_nam(extract, lats, lons, plotname)
        append_fort22(path, interpolated)
        # result.append(interpolated)
    #
    # return result
def file_single_84(date, forecast_production_hr, extension):
    return f'subset_{date}_nam.t{forecast_production_hr}z.awip1200.tm00{extension}'

def file_generator_84(date, forecast_production_hr, extension):
    #subset_20220313_nam.t00z.awip1200.tm00.grib2
    nam_files = [f'subset_{date}_nam.t{forecast_production_hr}z.awip12{str(forecasting_hour).zfill(2)}.tm00{extension}' for forecasting_hour in range(0, 37)]
    nam_files_2 = [f'subset_{date}_nam.t{forecast_production_hr}z.awip12{str(forecasting_hour).zfill(2)}.tm00{extension}' for forecasting_hour in range(39, 85, 3)]
    nam_urls_complete = nam_files + nam_files_2
    for f in nam_urls_complete:
        yield f

# def file_generator(start, stop, step, sequential):
#     from datetime import timedelta
#     t_start = start
#     counter_for_sequential = 0
#     # subset_20220313_nam.t00z.awip1200.tm00.grib2
#     while start < stop:
#         start = start + timedelta(hours=step)
#         if sequential:
#             file = 'nam_218_' + t_start.strftime("%Y%m%d") + '_0000_0' + "{:02d}".format(counter_for_sequential)
#             counter_for_sequential += step
#         else:
#             file = 'nam_218_' + start.strftime("%Y%m%d") + '_0000_0' + start.strftime("%H")
#         yield file

def append_fort22(path, interpolated):
    with open(path+'fort.22', mode='a', newline='') as file:
        towrite: str = ''
        for row in interpolated:
            towrite += '%.6f %.6f %.6f\n' % (row[0], row[1], row[2])
        # print(towrite)
        file.write(towrite)


def print_fort22(result):
    with open('fort.22', mode='w', newline='') as file:
        towrite: str = ''
        # print(len(result))
        for component in result:
            # print(len(component))
            for row in component:
                # print(row)
                towrite += '%.6f %.6f %.6f\n' % (row[0], row[1], row[2])
        file.write(towrite)

def interpolate_nam(table, lats, lons, plotname):
    '''
    :param table: ucomp, vcomp, press
    :param lats:
    :param lons:
    :return:
    '''
    ucomp, vcomp, press = table
    # print(ucomp)
    x = lons
    y = lats

    # xi = np.arange(-101, -76, 0.25)
    # yi = np.arange(18, 32, 0.25)
    xi = np.arange(-101, -76, 0.05)
    yi = np.arange(18, 32, 0.05)

    xi, yi = np.meshgrid(xi, yi)

    # interpolate
    ucompi = griddata((x, y), ucomp, (xi, yi), method='linear')
    vcompi = griddata((x, y), vcomp, (xi, yi), method='linear')
    pressi = griddata((x, y), press, (xi, yi), method='linear')

    # #plot
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # # plt.contourf(xi, yi, zi, np.arange(0, 1500, 10))
    # plt.contourf(xi, yi, ucompi, np.arange(ucomp.min() - 1, ucomp.max() + 1, .5))
    # plt.colorbar(orientation="vertical", pad=0.2)
    # plt.plot(-97.497482, 25.901747,'k.')
    # plt.xlabel('xi', fontsize=16)
    # plt.ylabel('yi', fontsize=16)
    # # plt.scatter(-97.497482, 25.901747, s=3)
    # print(plotname+'.png')
    # # plt.savefig(plotname+'.png', dpi=100)
    # # plt.show()
    # plt.close(fig)
    # #plot

    ucompi[np.isnan(ucompi)] = 0
    vcompi[np.isnan(vcompi)] = 0
    pressi[np.isnan(pressi)] = 0

    ucompi = np.flipud(ucompi)
    vcompi = np.flipud(vcompi)
    pressi = np.flipud(pressi)

    print(ucompi.shape)

    ucompiflat = ucompi.flatten()
    print(ucompiflat.shape)
    # print(ucompiflat[:100])
    # print(ucompi[:2])
    vcompiflat = vcompi.flatten()
    pressiflat = pressi.flatten()
    print(vcompiflat.shape)
    print(pressiflat.shape)


    mergedi = []
    for i in range(len(ucompiflat)):
        mergedi.append([ucompiflat[i], vcompiflat[i], pressiflat[i]])
    return mergedi


def extract_nam2(nam):
    '''
    :param nam: An opened nam grb at a certain time.
    :return: Returns a merged list with ucomp, vcomp and press at a certan time (of nam grib).
    '''
    naminfo = nam.select()[8], nam.select()[9], nam.select()[2]

    ucomp, lats, lons = naminfo[0].data(lat1=18, lat2=32, lon1=-101, lon2=-76)
    # print(naminfo[0], ucomp.shape, lats.shape, lons.shape)
    # ucomp, lats, lons = ucomp[:26441], lats[:26441], lons[:26441]
    # print(ucomp.shape)

    vcomp, lats, lons = naminfo[1].data(lat1=18, lat2=32, lon1=-101, lon2=-76)
    # print(naminfo[1], vcomp.shape, lats.shape, lons.shape)
    # vcomp = vcomp[:26441]

    press, lats, lons = naminfo[2].data(lat1=18, lat2=32, lon1=-101, lon2=-76)
    # press = press[:26441]

    merged = []
    for i in range(len(ucomp)):
        merged.append([ucomp[i], vcomp[i], press[i]])
    return merged


def niceplot():
    nam = pgrib.ndfd_open('/home/cesar/Documents/NAM/nam_218_20080723_0000_000.grb2')
    naminfo = nam.select()[8], nam.select()[9], nam.select()[2]
    print(naminfo)
    #
    ucomponent = naminfo[0]
    #
    ucomp, lats, lons = ucomponent.data(lat1=18, lat2=32, lon1=-101, lon2=-76)
    print(ucomp.max(), ucomp.min())
    # merge = extract_nam2(nam)

    # data coordinates and values
    # x = np.random.uniform(-101, -76, 25000)
    # y = np.random.uniform(18, 32, 25000)
    # z = np.random.uniform(0, 1500, 25000)

    x = lons
    y = lats
    z = ucomp

    # target grid to interpolate to
    # xi = np.arange(-101, -76, 0.05)
    # yi = np.arange(18, 32, 0.05)

    xi = np.arange(-101, -76, 0.05)
    yi = np.arange(18, 32, 0.05)


    xi,yi = np.meshgrid(xi, yi)

    # set mask
    # mask = (xi > 0.5) & (xi < 0.6) & (yi > 0.5) & (yi < 0.6)

    # interpolate
    zi = griddata((x,y),z,(xi,yi),method='linear')

    # mask out the field
    # zi[mask] = np.nan

    # plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plt.contourf(xi, yi, zi, np.arange(0, 1500, 10))
    plt.contourf(xi, yi, zi, np.arange(ucomp.min() - 1, ucomp.max()+1, .5))
    plt.colorbar(orientation="vertical", pad=0.2)
    # plt.plot(x,y,'k.')
    plt.xlabel('xi',fontsize=16)
    plt.ylabel('yi',fontsize=16)
    plt.savefig('interpolated.png',dpi=100)
    plt.show()
    # plt.close(fig)


# niceplot()

# print_fort22(grab_fcst(0, 85, 3))

# print_fort22(grab_fcst(0, 192, 3))

# print_fort22(grab_fcst(0, 360, 3))


# grab_fcst('2008072000', '2008082021', 3)
# grab_fcst('2018053121', '2018120100', 3)




# grab_fcst(1, 121, 1)



#create nd array
# array = np.arange(250).reshape(10, 25)
# arrayflat = array.flatten()
# print(array)
# print(arrayflat)

# print_fort22(grab_fcst(0, 24, 1))

# print_fort22(grab_fcst(0, 1, 1))



# starth, endh, step = 0, 1, 1
#
# result = []
# nam = pgrib.ndfd_open('/home/cesar/Documents/NAM/nam_218_20080723_0000_000.grb2')
# naminfo = nam.select()[8], nam.select()[9], nam.select()[2]
#
# ucomponent = naminfo[0]
#
# ucomp, lats, lons = ucomponent.data(lat1=18, lat2=32, lon1=-101, lon2=-76)
#
#
# for i in range(starth, endh, step):
#     hour = str(i).zfill(3)
#     nam = pgrib.ndfd_open('/home/cesar/Documents/NAM/nam_218_20080723_0000_' + str(hour) + '.grb2')
#     print('EXTRACTING /home/cesar/Documents/NAM/nam_218_20080723_0000_' + str(hour) + '.grb2')
#     extract = extract_nam(nam)
#     print('INTERPOLATING /home/cesar/Documents/NAM/nam_218_20080723_0000_' + str(hour) + '.grb2')
#
#     interpolated = interpolate_nam(extract, lats, lons)
#
#     result.append(interpolated)






# nams = nam.select(name='Pres')
# nampressure = nam.select(name='Surface pressure')
# namucomp = nam.select(name='10 metre U wind component')
# namvcomp = nam.select(name='10 metre V wind component')




# for i in range(len(lats)):
#     print(lats[i-1] - lats[i])

#
# lats, lons = naminfo[2].latlons()
# merged = merge_lats_lons(lats, lons)
# # print(naminfo[2], press.shape, lats.shape, lons.shape)
# print(lats.shape)
# print(lons.shape)
# print(len(merged))
# for merge in merged:
#     print(merge)

# press, lats, lons = naminfo[2].data(lat1=18, lat2=32, lon1=-101, lon2=-76)
# # press, lats, lons = naminfo[2].data(lat1=26, lat2=28, lon1=-101, lon2=-76)
# print(naminfo[2], press.shape, lats.shape, lons.shape)

# print(lons.max(), lons.min())

#
# merged = []
# counter = 0
# for l in range(len(lons)):
#     if lons[l-1] - lons[l] > 1:
#         counter += 1
#         print(lons[l-1], lons[l])
# merged = []
# for i in range(len(lats)):
#     merged.append([lats[i], lons[i]])
# print(len(merged))
# print(counter)
# plot(merged)


'''
Number of values in x: 500 
minimum x: -101
x increment: 0.05
number of values in y: 280
maximum y: 32
y increment: .05
time interval: 10800 sec (3 hours)
'''





