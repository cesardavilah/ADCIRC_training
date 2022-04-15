from ftplib import FTP
import os
import re  # Used to search for a string in a line
import requests  # Used to check if a URL exists
# import pygrib
import csv
from scipy.interpolate import griddata
import datetime
import time
import shutil
import sys
# from pydsstools.core import TimeSeriesContainer,UNDEFINED
# from pydsstools.heclib.dss import HecDss



def helper_download_HRRR_subset(date, url, searchString, SAVEDIR='./', dryrun=False):
    """
    Download a subset of GRIB fields from a HRRR file.

    This assumes there is an index (.idx) file available for the file.

    Parameters
    ----------
    url : string
        The URL for the HRRR file you are trying to download. There must be an
        index file for the GRIB2 file. For example, if
        ``url='https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20200624/hrrr.t01z.wrfsfcf17.grib2'``,
        then ``https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20200624/hrrr.t01z.wrfsfcf17.grib2.idx``
        must also exist on the server.
    searchString : str
        The string you are looking for in each line of the index file.
        Take a look at the
        .idx file at https://pando-rgw01.chpc.utah.edu/hrrr/sfc/20200624/hrrr.t01z.wrfsfcf17.grib2.idx
        to get familiar with what is in each line.
        Also look at this webpage: http://hrrr.chpc.utah.edu/HRRR_archive/hrrr_sfc_table_f00-f01.html
        for additional details.**You should focus on the variable and level
        field for your searches**.

        You may use regular expression syntax to customize your search.
        Check out this regulare expression cheatsheet:
        https://link.medium.com/7rxduD2e06

        Here are a few examples that can help you get started

        ================ ===============================================
        ``searchString`` Messages that will be downloaded
        ================ ===============================================
        ':TMP:2 m'       Temperature at 2 m.
        ':TMP:'          Temperature fields at all levels.
        ':500 mb:'       All variables on the 500 mb level.
        ':APCP:'         All accumulated precipitation fields.
        ':UGRD:10 m:'    U wind component at 10 meters.
        ':(U|V)GRD:'     U and V wind component at all levels.
        ':.GRD:'         (Same as above)
        ':(TMP|DPT):'    Temperature and Dew Point for all levels .
        ':(TMP|DPT|RH):' TMP, DPT, and Relative Humidity for all levels.
        ':REFC:'         Composite Reflectivity
        ':surface:'      All variables at the surface.
        ================ ===============================================

    SAVEDIR : string
        Directory path to save the file, default is the current directory.
    dryrun : bool
        If True, do not actually download, but print out what the function will
        attempt to do.

    Returns
    -------
    The path and name of the new file.
    """


    # Make SAVEDIR if path doesn't exist
    if not os.path.exists(SAVEDIR):
        os.makedirs(SAVEDIR)
        print(f'Created directory: {SAVEDIR}')

    # Make a request for the .idx file for the above URL
    idx = url + '.idx'
    r = requests.get(idx)

    # Check that the file exists. If there isn't an index, you will get a 404 error.
    if not r.ok:
        print('❌ SORRY! Status Code:', r.status_code, r.reason)
        print(f'❌ It does not look like the index file exists: {idx}')

    # Read the text lines of the request
    lines = r.text.split('\n')

    # Search expression
    expr = re.compile(searchString)

    # Store the byte ranges in a dictionary
    #     {byte-range-as-string: line}
    byte_ranges = {}
    for n, line in enumerate(lines, start=1):
        # n is the line number (starting from 1) so that when we call for
        # `lines[n]` it will give us the next line. (Clear as mud??)

        # Use the compiled regular expression to search the line
        if expr.search(line):
            # aka, if the line contains the string we are looking for...

            # Get the beginning byte in the line we found
            parts = line.split(':')
            rangestart = int(parts[1])

            # Get the beginning byte in the next line...
            if n + 1 < len(lines):
                # ...if there is a next line
                parts = lines[n].split(':')
                rangeend = int(parts[1])
            else:
                # ...if there isn't a next line, then go to the end of the file.
                rangeend = ''

            # Store the byte-range string in our dictionary,
            # and keep the line information too so we can refer back to it.
            byte_ranges[f'{rangestart}-{rangeend}'] = line

    # What should we name the file we save this data to?
    # Let's name it something like `subset_20200624_hrrr.t01z.wrfsfcf17.grib2`
    # runDate = list(byte_ranges.items())[0][1].split(':')[2][2:-2]
    runDate = date
    outFile = '_'.join(['subset', runDate, url.split('/')[-1]])
    outFile = os.path.join(SAVEDIR, outFile)

    for i, (byteRange, line) in enumerate(byte_ranges.items()):

        if i == 0:
            # If we are working on the first item, overwrite the existing file.
            curl = f'curl -s --ssl-no-revoke --range {byteRange} {url} > {outFile}'
        else:
            # If we are working on not the first item, append the existing file.
            curl = f'curl -s --ssl-no-revoke --range {byteRange} {url} >> {outFile}'

        num, byte, date, var, level, forecast, _ = line.split(':')

        if dryrun:
            print(f'  🌵 Dry Run: Found GRIB line [{num}]: variable={var}, level={level}, forecast={forecast}')
            print(f'  🌵 Dry Run: `{curl}`')
        else:
            print(f'  Downloading GRIB line [{num}]: variable={var}, level={level}, forecast={forecast}')
            os.system(curl)

    if dryrun:
        print(f'🌵 Dry Run: Success! Searched for [{searchString}] and found [{len(byte_ranges)}] GRIB fields.')
        print(f'🌵 Dry Run: Would save as {outFile}')
    else:
        print(f'✅ Success! Searched for [{searchString}] and got [{len(byte_ranges)}] GRIB fields.')
        print(f'    Saved as {outFile}')

        return outFile

def download_latest_NAM(searchString, date, SAVEDIR='./'):

    # NAM_ftp = 'ftp.ncep.noaa.gov'
    # ftp_con = FTP(NAM_ftp)
    # ftp_con.login()
    # print(ftp_con.pwd())
    # # ftp_con.cwd('/data/nccf/com/nam/prod')
    # ftp_con.cwd('/data/nccf/')
    # lists = []
    # ftp_con.dir(lists.append)
    #
    # available = lists[0].split()[-1:][0], lists[1].split()[-1:][0]
    # print("available:" + str(available))
    #
    # download = '/data/nccf/com/nam/prod/' + f"nam.{date}" + "/conus/"
    # ftp_con.cwd(download)
    #
    # lists = []
    # ftp_con.dir(download, lists.append)
    #
    # to_download = []
    # server = 'https://nomads.ncep.noaa.gov'
    # pwd = ftp_con.pwd() + '/'
    baselink = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/nam/prod'

    # for line in lists:
    #     if (line.find('awip12') != -1 and line.find('.grib2.idx') < 0 and line.find('t00z') != -1):
    #         to_download.append(server+pwd+line.split()[-1:][0])

    to_download = []

    nam_urls = [baselink+ f'/nam.{date}' + f'/nam.t00z.awip12{str(forecasting_hour).zfill(2)}.tm00.grib2' for forecasting_hour in range (0, 37)]
    nam_urls_2 = [baselink + f'/nam.{date}' + f'/nam.t00z.awip12{str(forecasting_hour).zfill(2)}.tm00.grib2' for
                forecasting_hour in range(39, 85, 3)]
    nam_urls_complete = nam_urls + nam_urls_2

    # print(nam_urls_complete)
    for n in nam_urls_complete:
        print(n)

    for nam in nam_urls_complete:
        helper_download_HRRR_subset(date, nam, searchString=searchString, SAVEDIR=SAVEDIR)
        time.sleep(1)


def load_points_CSV(filename):
    table = []
    with open(filename) as csv_f:
        csv_reader = csv.reader(csv_f, delimiter=',')
        for row in csv_reader:
            row.append([])
            table.append(row)
            # print(row)
    return table

def interpolate_nam(prate, lats, lons, point):
    x = lons
    y = lats

    # x for lons, y for lats
    xi, yi = point[0], point[1]

    # interpolate
    pratei = griddata((x, y), prate, (xi, yi), method='nearest')
    return pratei

def get_current_date():
    return datetime.datetime.today().strftime('%Y%m%d')

def flush(dir):

    # dir = 'path/to/dir'
    for files in os.listdir(dir):
        path = os.path.join(dir, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)

def prep_for_vcore(directory, arg):
    import logging
    import os
    import sys
    import numpy as np

    from fortreader import fort74, fort73, fort64, fort63, fort22, fort14, fort13, cesar_fort22

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    # if __name__ == '__main__':
    #
    # if len(arg) > 4 or len(arg) < 4:
    #     print('Usage: %s dir timeSlice' % (sys.argv[0]))
    #     print('-' * 80)
    #     print('dir       : Searches for fort 14, 63, 64, 73, and 74 in the specified directory')
    #     print('timeSlice : Sets slice to use for fort 63, 64, 73, 74')
    #     print('toggleBit : Set to 0 if sara, 1 if cesar')
    #     exit(-1)

    forts_dir = os.path.join('.', arg[0])
    time_slice = int(arg[1])
    toggle_bit = int(arg[2])

    # Hacky Solution for now
    wind_velocity = wind_pressure = wave_velocity = waves_array = hurricane_data = hurricane_course = nodal_attr = node_array = triangles = None

    # wind_velocity = fort74.read_fort74(os.path.join(forts_dir, 'fort.74'), time_slice)
    # wind_pressure = fort73.read_fort73(os.path.join(forts_dir, 'fort.73'), time_slice)
    # wave_velocity = fort64.read_fort64(os.path.join(forts_dir, 'fort.64'))
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

        with open(f'{forts_dir}/fort63.xyz', 'w') as xyz:
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

    # sys.argv = [directory, '83', '-1']
    # exec(open('/home/cesar/PycharmProjects/CMPautomation/ADCIRCController/Production/visualize_adcirc.py').read())
    os.chdir(directory)
    os.system(f'sed "s/ /,/g" {directory+"/"}fort63.xyz > {directory+"/"}fort63.csv')
    os.system('gdal_grid -zfield field_3 -txe -97.6688234727488549 -95.9583619884986803 -tye 26.0010747185894786 27.1244897802529046 -a invdistnn:smoothing=0.1:radius=0.002:max_points=3:nodata=-99 -tr 0.001 0.001 -of GTiff -ot Float64 -l fort63 dem.vrt dem.tiff')
    time.sleep(60)

    url = "https://vcore.utrgv.edu/adcirc"
    key = "3c6448c6-ef30-4046-878a-6acf0d8a9226"

    files = {'adcirc': ('dem.tiff', open(f'{directory+"//"}dem.tiff', 'rb'))}
    r = requests.post(url, headers={'key': key}, files=files)
    print(r.content)





# def write_to_dss(points, dss_file):
#     for point in points:
#         print(point[2])
#         pathname = "//" + point[2] + "/PRECIP-INC/26JUL2020/1HOUR/GAGE/"
#         print(pathname)
#
#         tsc = TimeSeriesContainer()
#         tsc.pathname = pathname
#         tsc.startDateTime = "26JUL2020 00:00:00"
#         tsc.numberValues = forecast_len
#         tsc.units = "IN"
#         tsc.type = "PER-CUM"
#         tsc.interval = 1
#         tsc.values = point[3]
#
#         fid = HecDss.Open(dss_file)
#         fid.deletePathname(tsc.pathname)
#         fid.put_ts(tsc)
#         ts = fid.read_ts(pathname)
#         fid.close()

#:(APCP|PRATE|CPOFP|PWAT):
# hrrr_latest = "20200626"
# hrrr_latest = "20201020"


# hrrr_latest = "20220207"
# hrrr_date = download_latest_NAM(searchString=":(U|V)GRD:10 m|PRES:surface:", SAVEDIR=r"/media/sf_SHARED_FOLDER_VM/temp_adcirc", date="20220207")




# hrrr_latest = hrrr_date[1].split('.')[1]


# points = load_points_CSV(r"C:\Users\c_sar\PycharmProjects\CMPautomation\Dataretrieval\points.csv")
# print(points)
# print(points)
# print(float(points[0][0]))

# forecast_len = 37
# for i in range(0, forecast_len):
#     print(fr"C:\Users\c_sar\Desktop\HRRR\subset_{hrrr_latest}_hrrr.t00z.wrfsfcf{i:02d}.grib2")
#     #open HRRR
#     grib = pygrib.open(fr"C:\Users\c_sar\Desktop\HRRR\subset_{hrrr_latest}_hrrr.t00z.wrfsfcf{i:02d}.grib2")
#
#     prate_grb = grib.select(name='Precipitation rate')[0]
#     # prate_grb = grib.select(name='Total Precipitation')[0]
#
#     #locate field to sample
#     prate, lats, lons = prate_grb.data(lat1=25, lat2=27, lon1=-99, lon2=-97)
#
#     #load field to memory and cut small piece around it
#
#     #interpolate
#
#
#     for point in points:
#         # print([float(point[0]), float(point[1])])
#         print("interpolating: "+point[2],end='')
#         point[3].append(101.7*(interpolate_nam(prate, lats, lons, [float(point[0]), float(point[1])])))
#         print("\tDONE ✅")
#
#
# for point in points:
#     print(point)

# dss_file = r"C:\Users\c_sar\Documents\HEC-DATA\HMS-FINISH-HIEN-NGUYEN\DSS HMS\example_watershed.dss"
# write_to_dss(points, dss_file=dss_file)








# import os
#
# def execute_hms(path_to_project, project_name, run_name, version="4.5"):
#     compute_script(path_to_project, project_name, run_name)
#     os.chdir(r'C:\Program Files\HEC\HEC-HMS\\'+version)
#     os.system(r'hec-hms.cmd -script '+path_to_project+'\compute.script')
#
#
# def compute_script(path_to_project, project_name, run_name):
#     path_to_project = path_to_project[:-1]
#     try:
#         os.chdir(path_to_project)
#         os.remove('compute.script')
#     except OSError:
#         pass
#     with open('compute.script', 'a') as file:
#         file.write("from hms.model import Project\nfrom hms import Hms\n")
#         path_to_project = path_to_project.replace('\\', r'\\')
#
#         file.write(r"myProject = Project.open('"+path_to_project+project_name+"')\n")
#         file.write("myProject.computeRun('"+run_name+"')\n")
#         file.write('myProject.close()\n')
#         file.write('Hms.shutdownEngine()\n')
#
# execute_hms(r'C:\Users\c_sar\Documents\HEC-DATA\HMS-FINISH-HIEN-NGUYEN\UTRGV_SUBBASIN\\', "UTRGV_SUBBASIN.hms", "DSS HANNA")
#
#
# dss_file = r"C:\Users\c_sar\Documents\HEC-DATA\HMS-FINISH-HIEN-NGUYEN\UTRGV_SUBBASIN\DSS_Hanna.dss"
# pathname = "//OUTLET 1/FLOW/01JUL2020/1HOUR/RUN:DSS HANNA/"
# startDate = "24JUL2020 0:00:00"
# endDate = "27JUL2020 12:00:00"



# from pydsstools.heclib.dss import HecDss
# import matplotlib.pyplot as plt
# import numpy as np
#
# fid = HecDss.Open(dss_file)
# ts = fid.read_ts(pathname,window=(startDate,endDate),trim_missing=False)
# print(ts)
#
# times = np.array(ts.pytimes)
# values = ts.values
# print(values)
# plt.plot(times[~ts.nodata],values[~ts.nodata],"o-")
# plt.gcf().autofmt_xdate()
# plt.show()
# fid.close()





